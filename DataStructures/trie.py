
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        node.is_end_of_word = True

    def search(self, word: str) -> bool:
        node = self.root

        for char in word:
            if char not in node.children:
                return False

            node = node.children[char]

        return node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        node = self.root

        for char in prefix:
            if char not in node.children:
                return False

            node = node.children[char]

        return True

    def delete(self, word: str) -> None:
        def helper(node, index):
            if index == len(word):
                if not node.is_end_of_word:
                    return False

                node.is_end_of_word = False
                return len(node.children) == 0

            char = word[index]

            if char not in node.children:
                return False

            should_delete = helper(node.children[char], index + 1)

            if should_delete:
                del node.children[char]

            return (
                not node.is_end_of_word
                and len(node.children) == 0
            )

        helper(self.root, 0)

