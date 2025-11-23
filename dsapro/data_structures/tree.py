# data_structures/tree.py
# A simple BST keyed by doctor name; each node contains a list of patient dicts for that doctor

class TreeNode:
    def __init__(self, doctor):
        self.doctor = doctor
        self.patients = []  # list of patient dicts
        self.left = None
        self.right = None

class PatientTree:
    def __init__(self):
        self.root = None

    def insert(self, doctor: str, patient_dict: dict):
        if not self.root:
            node = TreeNode(doctor)
            node.patients.append(patient_dict)
            self.root = node
            return

        cur = self.root
        while True:
            if doctor == cur.doctor:
                cur.patients.append(patient_dict)
                return
            elif doctor < cur.doctor:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = TreeNode(doctor)
                    cur.left.patients.append(patient_dict)
                    return
            else:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = TreeNode(doctor)
                    cur.right.patients.append(patient_dict)
                    return

    def search(self, doctor: str):
        cur = self.root
        while cur:
            if doctor == cur.doctor:
                return cur.patients.copy()
            elif doctor < cur.doctor:
                cur = cur.left
            else:
                cur = cur.right
        return []

    def remove(self, doctor: str, patient_id: int):
        # find node
        cur = self.root
        while cur:
            if doctor == cur.doctor:
                cur.patients = [p for p in cur.patients if p["patient_id"] != patient_id]
                return True
            elif doctor < cur.doctor:
                cur = cur.left
            else:
                cur = cur.right
        return False

    def inorder(self, node=None, res=None):
        if res is None:
            res = []
        if node is None:
            node = self.root
        if not node:
            return res
        if node.left:
            self.inorder(node.left, res)
        res.append((node.doctor, node.patients.copy()))
        if node.right:
            self.inorder(node.right, res)
        return res

    def rebuild_from_list(self, patient_list):
        # patient_list: list of patient dicts
        self.root = None
        for p in patient_list:
            self.insert(p["doctor"], p)