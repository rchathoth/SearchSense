class TSTNode:

    def __init__(self, char: str):
        self.char = char
        self.left = None
        self.middle = None
        self.right = None
        self.is_end_of_word = False


class TST:

    def __init__(self):
        self.root = None
        self._contains_empty_string = False

    def insert(self, word: str) -> None:
        """Add *word* to the trie."""
        if word == "":
            self._contains_empty_string = True
            return

        def insert_at(node, index):
            char = word[index]
            if node is None:
                node = TSTNode(char)

            if char < node.char:
                node.left = insert_at(node.left, index)
            elif char > node.char:
                node.right = insert_at(node.right, index)
            elif index + 1 < len(word):
                node.middle = insert_at(node.middle, index + 1)
            else:
                node.is_end_of_word = True
            return node

        self.root = insert_at(self.root, 0)

    def _find_node(self, text: str):
        if not text:
            return None

        node = self.root
        index = 0
        while node is not None:
            char = text[index]
            if char < node.char:
                node = node.left
            elif char > node.char:
                node = node.right
            elif index + 1 == len(text):
                return node
            else:
                index += 1
                node = node.middle
        return None

    def search(self, word: str) -> bool:
        if word == "":
            return self._contains_empty_string
        node = self._find_node(word)
        return node is not None and node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        if prefix == "":
            return self._contains_empty_string or self.root is not None
        node = self._find_node(prefix)
        return node is not None and (node.is_end_of_word or node.middle is not None)

    def delete(self, word: str) -> None:
        if word == "":
            self._contains_empty_string = False
            return

        def is_leaf(node):
            return node.left is None and node.middle is None and node.right is None

        def remove(node, index):
            if node is None:
                return None

            char = word[index]
            if char < node.char:
                node.left = remove(node.left, index)
            elif char > node.char:
                node.right = remove(node.right, index)
            elif index + 1 < len(word):
                node.middle = remove(node.middle, index + 1)
            else:
                node.is_end_of_word = False

            # A node can only be discarded when it has no role in any path.
            if not node.is_end_of_word and is_leaf(node):
                return None
            return node

        self.root = remove(self.root, 0)
