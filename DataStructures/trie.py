
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.product_ids = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, product_id: int) -> None:
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()

            node = node.children[char]

        node.is_end_of_word = True

        if len(node.product_ids) == 0 or node.product_ids[-1] != product_id:
            node.product_ids.append(product_id)

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

    def _find_node(self, prefix: str):
        node = self.root

        for char in prefix:
            if char not in node.children:
                return None

            node = node.children[char]

        return node

    def _collect_words(self, node, prefix: str, results: list) -> None:
        if node.is_end_of_word:
            results.append((prefix, node.product_ids))

        # Go through the letters in order so the words come out alphabetical, same as the TST.
        for char in sorted(node.children):
            self._collect_words(node.children[char], prefix + char, results)

    def _words_with_prefix(self, prefix: str) -> list:
        if prefix == "":
            return []

        node = self._find_node(prefix)
        if node is None:
            return []

        words = []
        self._collect_words(node, prefix, words)
        return words

    def prefix_search(self, prefix: str) -> list:
        words = self._words_with_prefix(prefix)

        # One product can have more than one word with this prefix, so skip repeats.
        seen = set()
        product_ids = []
        for word, ids in words:
            for product_id in ids:
                if product_id not in seen:
                    seen.add(product_id)
                    product_ids.append(product_id)
        return product_ids

    def autocomplete(self, prefix: str, k: int) -> list:
        words = self._words_with_prefix(prefix)

        words.sort(key=lambda pair: len(pair[1]), reverse=True)

        suggestions = []
        for word, ids in words[:k]:
            suggestions.append(word)
        return suggestions

    def delete(self, word: str) -> None:
        def helper(node, index):
            if index == len(word):
                if not node.is_end_of_word:
                    return False

                node.is_end_of_word = False
                node.product_ids = []
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

