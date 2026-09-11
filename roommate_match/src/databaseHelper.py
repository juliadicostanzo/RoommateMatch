from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .admin import Admin
from .Student import Student
from .pairing import pairing
from .roommateRequest import roommateRequest
from .system import RoommateSystem


_PENDING_INTEREST_UPDATES: dict[int, dict[int, set[str]]] = {}
_PENDING_PREFERENCE_UPDATES: dict[int, dict[int, set[str]]] = {}


# -----------------------------------------------------------------------------
# Loading / saving helpers
# -----------------------------------------------------------------------------


def get_default_database_path() -> Path:
	return Path(__file__).resolve().parents[2] / "app.db"


def connect_database(database_path: str | Path | None = None) -> sqlite3.Connection:
	path = Path(database_path) if database_path is not None else get_default_database_path()
	return sqlite3.connect(path)


def create_system_from_database(connection: sqlite3.Connection) -> RoommateSystem:
	system = RoommateSystem()
	_populate_students(connection, system)
	_populate_admins(connection, system)
	_populate_roommate_requests(connection, system)
	_populate_interest_options(connection, system)
	_populate_preference_options(connection, system)
	return system


def bootstrap_database_and_system(
	database_path: str | Path | None = None,
) -> tuple[sqlite3.Connection, RoommateSystem]:
	connection = connect_database(database_path)
	ensure_roommate_requests_table(connection)
	system = create_system_from_database(connection)
	return connection, system


def ensure_roommate_requests_table(connection: sqlite3.Connection) -> None:
	connection.execute(
		"""
		CREATE TABLE IF NOT EXISTS roommate_requests (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			group_request_id INTEGER NOT NULL DEFAULT 0,
			sender_id INT NOT NULL,
			receiver_id INT NOT NULL,
			status TEXT NOT NULL DEFAULT 'pending',
			created_at TEXT DEFAULT CURRENT_TIMESTAMP,
			updated_at TEXT DEFAULT CURRENT_TIMESTAMP
		)
		"""
	)
	_request_add_column_if_missing(connection, "roommate_requests", "group_request_id", "INTEGER NOT NULL DEFAULT 0")
	connection.execute(
		"UPDATE roommate_requests SET group_request_id = id WHERE group_request_id = 0"
	)
	connection.commit()


def _request_add_column_if_missing(
	connection: sqlite3.Connection,
	table_name: str,
	column_name: str,
	column_definition: str,
) -> None:
	columns = _table_columns(connection, table_name)
	if column_name in columns:
		return

	connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def create_roommate_request(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	request: roommateRequest,
) -> tuple[bool, str]:
	sender_id = int(request.getSenderId())
	receiver_ids = [int(receiver_id) for receiver_id in request.getReceiverIds()]

	if len(receiver_ids) == 0:
		return False, "Select at least one student."

	if len(receiver_ids) > 3:
		return False, "A group request can have at most 3 other students."

	if sender_id in receiver_ids:
		return False, "You cannot send a request to yourself."

	receiver_ids = list(dict.fromkeys(receiver_ids))
	if len(receiver_ids) == 0:
		return False, "Select at least one student."

	group_size = 1 + len(receiver_ids)
	if group_size > 4:
		return False, "A group can have at most 4 people."

	active_member_ids: set[int] = set()
	for queued_request in system.requests:
		if _request_model_status(queued_request) not in {"pending", "accepted"}:
			continue
		active_member_ids.add(int(queued_request.getSenderId()))
		active_member_ids.update(int(receiver_id) for receiver_id in queued_request.getReceiverIds())

	if sender_id in active_member_ids:
		return False, "You already have an active roommate request group."

	conflicting_ids = [receiver_id for receiver_id in receiver_ids if receiver_id in active_member_ids]
	if conflicting_ids:
		return False, "One or more selected students are already in your active group or pending requests."

	new_request = roommateRequest(sender_id, receiver_ids[0], *receiver_ids[1:3])
	_set_request_id(new_request, _next_group_request_id(system))
	system.requests.append(new_request)
	return True, "Roommate request queued. Save and Exit to persist."


def persist_pending_roommate_requests(connection: sqlite3.Connection, system: RoommateSystem) -> int:
	ensure_roommate_requests_table(connection)
	connection.execute("DELETE FROM roommate_requests")

	requests = list(system.requests)
	for index, request in enumerate(requests, start=1):
		sender_id = int(request.getSenderId())
		receiver_ids = [int(receiver_id) for receiver_id in request.getReceiverIds()]
		if not receiver_ids:
			continue

		request_id = _request_id(request, default=index)
		for receiver_id in receiver_ids:
			response = request.responses.get(receiver_id)
			status = "pending"
			if response is True:
				status = "accepted"
			elif response is False:
				status = "rejected"

			connection.execute(
				"""
				INSERT INTO roommate_requests (group_request_id, sender_id, receiver_id, status)
				VALUES (?, ?, ?, ?)
				""",
				(int(request_id), sender_id, receiver_id, status),
			)

	connection.commit()
	return len(requests)


def persist_pending_interest_updates(connection: sqlite3.Connection) -> int:
	pending_interest_updates = _pending_interest_updates_for_connection(connection)
	if not pending_interest_updates:
		return 0

	join_table = _get_interest_join_table(connection)
	columns = _table_columns(connection, join_table)
	written_students = 0

	for student_id, interest_titles in pending_interest_updates.items():
		connection.execute(f"DELETE FROM {join_table} WHERE student_id = ?", (int(student_id),))

		interest_ids: list[int] = []
		for interest_title in sorted(interest_titles):
			interest_id = _find_interest_id(connection, interest_title)
			if interest_id is not None:
				interest_ids.append(int(interest_id))

		if interest_ids:
			if "id" in columns:
				next_id_row = connection.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {join_table}").fetchone()
				next_id = int(next_id_row[0]) if next_id_row is not None else 1
				for interest_id in interest_ids:
					connection.execute(
						f"INSERT INTO {join_table} (id, student_id, interest_id) VALUES (?, ?, ?)",
						(next_id, int(student_id), interest_id),
					)
					next_id += 1
			else:
				for interest_id in interest_ids:
					connection.execute(
						f"INSERT INTO {join_table} (student_id, interest_id) VALUES (?, ?)",
						(int(student_id), interest_id),
					)

		written_students += 1

	connection.commit()
	pending_interest_updates.clear()
	return written_students


def persist_pending_preference_updates(connection: sqlite3.Connection) -> int:
	pending_preference_updates = _pending_preference_updates_for_connection(connection)
	if not pending_preference_updates:
		return 0

	if not _table_exists(connection, "student_preferences"):
		return 0

	columns = _table_columns(connection, "student_preferences")
	written_students = 0

	for student_id, preference_titles in pending_preference_updates.items():
		connection.execute("DELETE FROM student_preferences WHERE student_id = ?", (int(student_id),))

		preference_names = sorted(preference_titles)
		if preference_names:
			if "id" in columns:
				next_id_row = connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM student_preferences").fetchone()
				next_id = int(next_id_row[0]) if next_id_row is not None else 1
				for preference_name in preference_names:
					connection.execute(
						"INSERT INTO student_preferences (id, student_id, preference) VALUES (?, ?, ?)",
						(next_id, int(student_id), preference_name),
					)
					next_id += 1
			else:
				for preference_name in preference_names:
					connection.execute(
						"INSERT INTO student_preferences (student_id, preference) VALUES (?, ?)",
						(int(student_id), preference_name),
					)

		written_students += 1

	connection.commit()
	pending_preference_updates.clear()
	return written_students


def persist_students(connection: sqlite3.Connection, system: RoommateSystem) -> int:
	if not _table_exists(connection, "students"):
		return 0

	student_columns = _table_columns(connection, "students")
	has_group_id = "group_id" in student_columns

	connection.execute("DELETE FROM students")
	for student in system.students:
		if has_group_id:
			connection.execute(
				"""
				INSERT INTO students (id, name, email, password, hometown, group_id)
				VALUES (?, ?, ?, ?, ?, ?)
				""",
				(
					int(student.id),
					str(student.name),
					str(student.email),
					str(student.password),
					str(student.hometown),
					int(student.groupID) if int(student.groupID) >= 0 else None,
				),
			)
		else:
			connection.execute(
				"""
				INSERT INTO students (id, name, email, password, hometown)
				VALUES (?, ?, ?, ?, ?)
				""",
				(
					int(student.id),
					str(student.name),
					str(student.email),
					str(student.password),
					str(student.hometown),
				),
			)

	connection.commit()
	return len(system.students)


def persist_approved_groups(connection: sqlite3.Connection, system: RoommateSystem) -> int:
	if not hasattr(system, "approved_groups"):
		return 0

	connection.execute(
		"""
		CREATE TABLE IF NOT EXISTS groups (
			id INTEGER PRIMARY KEY
		)
		"""
	)

	inserted = 0
	for approved_group in system.approved_groups:
		group_id = int(getattr(approved_group, "group_id", -1))
		if group_id < 0:
			continue

		exists = connection.execute("SELECT 1 FROM groups WHERE id = ?", (group_id,)).fetchone()
		if exists is not None:
			continue

		connection.execute("INSERT INTO groups (id) VALUES (?)", (group_id,))
		inserted += 1

	connection.commit()
	return inserted


def get_interest_options(connection: sqlite3.Connection) -> list[tuple[int, str]]:
	if not _table_exists(connection, "interests"):
		return []

	rows = connection.execute("SELECT id, title FROM interests ORDER BY title").fetchall()
	return [
		(int(row[0]), str(row[1]))
		for row in rows
		if row
		and row[0] is not None
		and row[1] is not None
		and str(row[1]).strip().lower() not in {"title", "interest"}
	]


def get_student_interest_titles(connection: sqlite3.Connection, student_id: int) -> list[str]:
	return _get_student_interest_titles(connection, student_id)


def add_interest_to_student(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	student: Student,
	interest_title: str,
) -> tuple[bool, str]:
	if interest_title not in system.interest_options:
		return False, "That interest does not exist."

	if interest_title in student.interests:
		return False, "Interest already exists in your profile."

	updated_interests = set(student.interests)
	updated_interests.add(interest_title)
	student.interests = sorted(updated_interests)

	pending_interest_updates = _pending_interest_updates_for_connection(connection)
	pending_interest_updates[int(student.id)] = set(student.interests)
	return True, "Interest added. Save and Exit to persist."


def remove_interest_from_student(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	student: Student,
	interest_title: str,
) -> tuple[bool, str]:
	if interest_title not in system.interest_options:
		return False, "That interest does not exist."

	if interest_title not in student.interests:
		return False, "Interest was not in your profile."

	updated_interests = set(student.interests)
	updated_interests.discard(interest_title)
	student.interests = sorted(updated_interests)

	pending_interest_updates = _pending_interest_updates_for_connection(connection)
	pending_interest_updates[int(student.id)] = set(student.interests)
	return True, "Interest removed. Save and Exit to persist."


def get_student_preference_titles(connection: sqlite3.Connection, student_id: int) -> list[str]:
	return _get_student_preferences(connection, student_id)


def add_preference_to_student(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	student: Student,
	preference_title: str,
) -> tuple[bool, str]:
	if preference_title not in system.preference_options:
		return False, "That preference does not exist."

	if preference_title in student.preferences:
		return False, "Preference already exists in your profile."

	updated_preferences = set(student.preferences)
	updated_preferences.add(preference_title)
	student.preferences = sorted(updated_preferences)

	pending_preference_updates = _pending_preference_updates_for_connection(connection)
	pending_preference_updates[int(student.id)] = set(student.preferences)
	return True, "Preference added. Save and Exit to persist."


def remove_preference_from_student(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	student: Student,
	preference_title: str,
) -> tuple[bool, str]:
	if preference_title not in system.preference_options:
		return False, "That preference does not exist."

	if preference_title not in student.preferences:
		return False, "Preference was not in your profile."

	updated_preferences = set(student.preferences)
	updated_preferences.discard(preference_title)
	student.preferences = sorted(updated_preferences)

	pending_preference_updates = _pending_preference_updates_for_connection(connection)
	pending_preference_updates[int(student.id)] = set(student.preferences)
	return True, "Preference removed. Save and Exit to persist."


# -----------------------------------------------------------------------------
# Helpers that use the database
# -----------------------------------------------------------------------------


def _pending_interest_updates_for_connection(connection: sqlite3.Connection) -> dict[int, set[str]]:
	connection_key = id(connection)
	if connection_key not in _PENDING_INTEREST_UPDATES:
		_PENDING_INTEREST_UPDATES[connection_key] = {}
	return _PENDING_INTEREST_UPDATES[connection_key]


def _pending_preference_updates_for_connection(connection: sqlite3.Connection) -> dict[int, set[str]]:
	connection_key = id(connection)
	if connection_key not in _PENDING_PREFERENCE_UPDATES:
		_PENDING_PREFERENCE_UPDATES[connection_key] = {}
	return _PENDING_PREFERENCE_UPDATES[connection_key]


def get_incoming_roommate_requests(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	receiver_id: int,
) -> list[dict[str, Any]]:
	requests: list[dict[str, Any]] = []
	seen_request_ids: set[int] = set()
	for request in system.requests:
		receiver_ids = [int(receiver) for receiver in request.getReceiverIds()]
		if int(receiver_id) not in receiver_ids:
			continue
		request_id = _request_id(request)
		if request_id in seen_request_ids:
			continue
		seen_request_ids.add(request_id)
		requests.append(
			{
				"request_id": request_id,
				"sender_id": int(request.getSenderId()),
				"receiver_ids": receiver_ids,
				"status": _request_model_status(request),
				"request": request,
			}
		)

	requests.sort(key=lambda request_row: int(request_row["request_id"]), reverse=True)
	return requests


def get_outgoing_roommate_requests(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	sender_id: int,
) -> list[dict[str, Any]]:
	requests: list[dict[str, Any]] = []
	for request in system.requests:
		if int(request.getSenderId()) != int(sender_id):
			continue
		status = _request_model_status(request)
		if status not in {"pending", "accepted"}:
			continue
		receiver_ids = [int(receiver) for receiver in request.getReceiverIds()]
		requests.append(
			{
				"request_id": _request_id(request),
				"sender_id": int(request.getSenderId()),
				"receiver_ids": receiver_ids,
				"status": status,
				"request": request,
			}
		)

	requests.sort(key=lambda request_row: int(request_row["request_id"]), reverse=True)
	return requests


def respond_to_roommate_request(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	request_id: int,
	accept: bool,
	responder_id: int | None = None,
) -> bool:
	if responder_id is None:
		return False

	request = _find_request_by_id(system, int(request_id))
	if request is None:
		return False

	request_receiver_ids = [int(receiver_id) for receiver_id in request.getReceiverIds()]
	if int(responder_id) not in request_receiver_ids:
		return False

	if accept:
		request.accept_request(int(responder_id))
	else:
		for receiver_id in request_receiver_ids:
			request.reject_request(int(receiver_id))

	request.updateStatus()
	if request.isAccepted() is False:
		system.requests = [
			existing_request
			for existing_request in system.requests
			if _request_id(existing_request) != int(request_id)
		]
	elif request.isAccepted() is True:
		update_request_list = getattr(system, "updateRequestList", None)
		if callable(update_request_list):
			update_request_list(request)
		else:
			group_id_generator = getattr(system, "generateGroupId", None)
			if not callable(group_id_generator):
				group_id_generator = getattr(system, "gerenateGroupId", None)
			if callable(group_id_generator):
				group_members = [int(request.getSenderId()), *[int(receiver_id) for receiver_id in request.getReceiverIds()]]
				system.pairings.append(pairing(int(group_id_generator()), group_members))
				system.requests = [
					existing_request
					for existing_request in system.requests
					if _request_id(existing_request) != int(request_id)
				]
	return True


def get_group_status_for_student(
	connection: sqlite3.Connection,
	system: RoommateSystem,
	student_id: int,
) -> list[dict[str, str]]:
	members: dict[str, dict[str, str]] = {}
	for request in system.requests:
		status = _request_model_status(request)
		if status not in {"pending", "accepted"}:
			continue

		sender_id = int(request.getSenderId())
		receiver_ids = [int(receiver) for receiver in request.getReceiverIds()]
		if int(student_id) != sender_id and int(student_id) not in receiver_ids:
			continue

		sender_key = str(sender_id)
		if sender_key not in members:
			members[sender_key] = {"id": sender_key, "status": "Accepted"}

		for receiver_id in receiver_ids:
			receiver_key = str(receiver_id)
			receiver_response = request.responses.get(receiver_id)
			receiver_status = "Pending"
			if receiver_response is True:
				receiver_status = "Accepted"
			elif receiver_response is False:
				receiver_status = "Rejected"

			if receiver_key not in members:
				members[receiver_key] = {"id": receiver_key, "status": receiver_status}
			elif members[receiver_key]["status"] != "Accepted":
				members[receiver_key]["status"] = receiver_status

	return list(members.values())


def _next_group_request_id(system: RoommateSystem) -> int:
	if not system.requests:
		return 1
	return max(_request_id(request) for request in system.requests) + 1


def _request_model_status(request: roommateRequest) -> str:
	responses = [request.responses.get(int(receiver_id)) for receiver_id in request.getReceiverIds()]
	if any(response is False for response in responses):
		return "rejected"
	if responses and all(response is True for response in responses):
		return "accepted"
	return "pending"


def _request_id(request: roommateRequest, default: int = 0) -> int:
	request_id = getattr(request, "request_id", default)
	return int(request_id)


def _set_request_id(request: roommateRequest, request_id: int) -> None:
	setattr(request, "request_id", int(request_id))


def _find_request_by_id(system: RoommateSystem, request_id: int) -> roommateRequest | None:
	for request in system.requests:
		if _request_id(request) == int(request_id):
			return request
	return None


def _populate_roommate_requests(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "roommate_requests"):
		return

	rows = connection.execute(
		"""
		SELECT group_request_id, sender_id, receiver_id, status
		FROM roommate_requests
		ORDER BY group_request_id DESC, id DESC
		"""
	).fetchall()

	grouped_rows: dict[int, dict[str, Any]] = {}
	for row in rows:
		group_request_id = int(row[0])
		sender_id = int(row[1])
		receiver_id = int(row[2])
		status = str(row[3])

		group = grouped_rows.setdefault(
			group_request_id,
			{"sender_id": sender_id, "receiver_ids": [], "status_by_receiver": {}},
		)
		if receiver_id not in group["receiver_ids"]:
			group["receiver_ids"].append(receiver_id)
		group["status_by_receiver"][receiver_id] = status

	system.requests = []
	for group_request_id in sorted(grouped_rows.keys(), reverse=True):
		group = grouped_rows[group_request_id]
		receiver_ids = list(group["receiver_ids"])
		if not receiver_ids:
			continue

		request = roommateRequest(int(group["sender_id"]), receiver_ids[0], *receiver_ids[1:3])
		_set_request_id(request, int(group_request_id))

		status_by_receiver: dict[int, str] = group["status_by_receiver"]
		for receiver_id in request.getReceiverIds():
			status = status_by_receiver.get(int(receiver_id), "pending")
			if status == "accepted":
				request.accept_request(int(receiver_id))
			elif status == "rejected":
				request.reject_request(int(receiver_id))

		request.updateStatus()
		if request.isAccepted() is False:
			continue
		system.requests.append(request)


def _get_interest_join_table(connection: sqlite3.Connection) -> str:
	join_table = _choose_interest_join_table(connection)
	if join_table is None:
		raise ValueError("Interests join table not found. Expected students_to_interests or students_to_interest.")
	return join_table


def _find_interest_id(connection: sqlite3.Connection, interest_title: str) -> int | None:
	if not _table_exists(connection, "interests"):
		return None

	row = connection.execute(
		"SELECT id FROM interests WHERE LOWER(title) = LOWER(?) LIMIT 1",
		(interest_title,),
	).fetchone()
	if row is None:
		return None
	return int(row[0])


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
	row = connection.execute(
		"SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
		(table_name,),
	).fetchone()
	return row is not None


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
	rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
	return {str(row[1]) for row in rows}


def _choose_interest_join_table(connection: sqlite3.Connection) -> str | None:
	if _table_exists(connection, "students_to_interests"):
		return "students_to_interests"
	if _table_exists(connection, "students_to_interest"):
		return "students_to_interest"
	return None


def _get_existing_groups(connection: sqlite3.Connection) -> dict[int, int]:
	groups: dict[int, int] = {}

	if _table_exists(connection, "students"):
		student_columns = _table_columns(connection, "students")
		if "group_id" in student_columns:
			rows = connection.execute(
				"SELECT id, group_id FROM students WHERE group_id IS NOT NULL"
			).fetchall()
			groups.update({int(student_id): int(group_id) for student_id, group_id in rows})

	if _table_exists(connection, "students_to_groups"):
		rows = connection.execute(
			"SELECT student_id, group_id FROM students_to_groups"
		).fetchall()
		groups.update({int(student_id): int(group_id) for student_id, group_id in rows})

	return groups


def _populate_students(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "students"):
		return

	rows = connection.execute(
		"SELECT id, name, email, password, hometown FROM students"
	).fetchall()
	groups_by_student = _get_existing_groups(connection)

	for row in rows:
		if _looks_like_header_row(row):
			continue

		student_id = int(row[0])
		student = Student(
			student_id,
			str(row[1]),
			str(row[2]),
			str(row[3]),
			str(row[4]),
		)
		student.groupID = groups_by_student.get(student_id, -1)
		student.interests = _get_student_interest_titles(connection, student_id)
		student.preferences = _get_student_preferences(connection, student_id)
		system.students.append(student)


def _populate_admins(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "admins"):
		return

	rows = connection.execute(
		"SELECT id, name, email, password FROM admins"
	).fetchall()

	system.admins = []
	for row in rows:
		if _looks_like_admin_header_row(row):
			continue
		system.admins.append(
			Admin(int(row[0]), str(row[1]), str(row[2]), str(row[3]), system)
		)


def _looks_like_admin_header_row(row: tuple[Any, ...]) -> bool:
	id_value = str(row[0]).strip().lower()
	name_value = str(row[1]).strip().lower()
	return id_value in {"id", "admin_id"} or name_value in {"name", "admin_name"}


def _looks_like_header_row(row: tuple[Any, ...]) -> bool:
	id_value = str(row[0]).strip().lower()
	name_value = str(row[1]).strip().lower()
	return id_value in {"id", "student_id"} or name_value in {"name", "student_name"}


def _get_student_interest_titles(connection: sqlite3.Connection, student_id: int) -> list[str]:
	join_table = _choose_interest_join_table(connection)
	if join_table is None or not _table_exists(connection, "interests"):
		return []

	rows = connection.execute(
		f"""
		SELECT i.title
		FROM {join_table} AS sti
		JOIN interests AS i ON i.id = sti.interest_id
		WHERE sti.student_id = ?
		ORDER BY i.title
		""",
		(student_id,),
	).fetchall()
	return [str(row[0]) for row in rows if row and row[0] is not None]


def _get_student_preferences(connection: sqlite3.Connection, student_id: int) -> list[str]:
	if _table_exists(connection, "students_to_preference") and _table_exists(connection, "preferences"):
		rows = connection.execute(
			"""
			SELECT p.title
			FROM students_to_preference AS stp
			JOIN preferences AS p ON p.id = stp.preference_id
			WHERE stp.student_id = ?
			ORDER BY p.title
			""",
			(student_id,),
		).fetchall()
		return [str(row[0]) for row in rows if row and row[0] is not None]

	if not _table_exists(connection, "student_preferences"):
		return []

	rows = connection.execute(
		"""
		SELECT preference
		FROM student_preferences
		WHERE student_id = ?
		ORDER BY preference
		""",
		(student_id,),
	).fetchall()
	return [str(row[0]) for row in rows if row and row[0] is not None]


def _populate_interest_options(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if not _table_exists(connection, "interests"):
		return

	rows = connection.execute("SELECT title FROM interests ORDER BY title").fetchall()
	system.interest_options = [
		str(row[0])
		for row in rows
		if row and row[0] is not None and str(row[0]).strip().lower() not in {"title", "interest"}
	]


def _populate_preference_options(connection: sqlite3.Connection, system: RoommateSystem) -> None:
	if _table_exists(connection, "preferences"):
		rows = connection.execute("SELECT title FROM preferences ORDER BY title").fetchall()
		system.preference_options = [
			str(row[0])
			for row in rows
			if row and row[0] is not None and str(row[0]).strip().lower() != "title"
		]
		return

	if not _table_exists(connection, "preference_options"):
		return

	rows = connection.execute("SELECT preference FROM preference_options ORDER BY preference").fetchall()
	system.preference_options = [
		str(row[0])
		for row in rows
		if row and row[0] is not None and str(row[0]).strip().lower() != "preference"
	]
