class IncorrectPagination(Exception):
    def __init__(self, page: int, page_size: int) -> None:
        super().__init__("Page must be >= 1 and page_size must be <= 500")
        self.page: int = page
        self.page_size: int = page_size
