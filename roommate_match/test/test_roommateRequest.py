import unittest
from roommate_match.src.roommateRequest import roommateRequest

class TestRoommateRequest(unittest.TestCase):

    def setUp(self):
        self.request1 = roommateRequest(1, 2)
        self.request2 = roommateRequest(3, 4, 5, 6)

    def test_initial_status(self):
        self.assertIsNone(self.request1.isAccepted())
        self.assertIsNone(self.request2.isAccepted())

    def test_accept_request(self):
        self.request1.accept_request(2)
        self.request1.updateStatus()
        self.assertTrue(self.request1.isAccepted())
        self.request2.accept_request(4)
        self.request2.updateStatus()
        self.assertIsNone((self.request2.isAccepted()))

    def test_reject_request(self):
        self.request2.reject_request(5)
        self.request2.updateStatus()
        self.assertFalse(self.request2.isAccepted())

    def test_get_sender_id(self):
        self.assertEqual(self.request1.getSenderId(), 1)
        self.assertFalse(self.request1.getSenderId() == 2)

        self.assertEqual(self.request2.getSenderId(), 3)
        self.assertFalse(self.request2.getSenderId() == 4)
        self.assertFalse(self.request2.getSenderId() == 5)
        self.assertFalse(self.request2.getSenderId() == 6)  

    def test_get_receiver_ids(self):
        self.assertEqual(self.request1.getReceiverIds(), [2])
        self.assertEqual(self.request2.getReceiverIds(), [4, 5, 6])

if __name__ == '__main__':
    unittest.main()