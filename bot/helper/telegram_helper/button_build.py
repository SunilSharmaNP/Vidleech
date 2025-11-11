from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class ButtonMaker:
    """
    Builds Telegram inline buttons with cleaner layout and auto-balancing columns.
    Compatible with existing user_settings and other modules.
    """

    def __init__(self):
        self._button = []
        self._header_button = []
        self._footer_button = []

    def reset(self):
        """Clears all stored buttons."""
        self._button.clear()
        self._header_button.clear()
        self._footer_button.clear()

    def button_link(self, key: str, link: str, position: str = None, style: str = None):
        """
        Add a button with an external URL.
        :param key: Display text
        :param link: Target URL
        :param position: header, footer, or default
        :param style: Optional visual hint (future)
        """
        key = self._style_text(key, style)
        button = InlineKeyboardButton(text=key, url=link)
        self._add_button(button, position)

    def button_data(self, key: str, data: str, position: str = None, style: str = None):
        """
        Add a button with callback data.
        :param key: Display text
        :param data: Callback data
        :param position: header, footer, or default
        :param style: Optional visual hint (future)
        """
        key = self._style_text(key, style)
        button = InlineKeyboardButton(text=key, callback_data=data)
        self._add_button(button, position)

    def _add_button(self, button: InlineKeyboardButton, position: str = None):
        """Appends the button to the correct section."""
        match position:
            case 'header':
                self._header_button.append(button)
            case 'footer':
                self._footer_button.append(button)
            case _:
                self._button.append(button)

    def _style_text(self, key: str, style: str = None) -> str:
        """Add optional visual styles."""
        if not style:
            return key.strip()

        match style.lower():
            case 'bold':
                return f"𝗕 {key}"
            case 'italic':
                return f"𝘐 {key}"
            case 'fancy':
                return f"★ {key} ★"
            case 'emoji':
                return f"• {key} •"
            case _:
                return key.strip()

    def build_menu(self, b_cols: int = 2, h_cols: int = 8, f_cols: int = 8) -> InlineKeyboardMarkup:
        """
        Build an InlineKeyboardMarkup object.
        Automatically centers buttons and maintains alignment across different menus.
        :param b_cols: Number of columns for main buttons
        :param h_cols: Columns for header buttons
        :param f_cols: Columns for footer buttons
        """
        # --- auto-balance layout ---
        total_buttons = len(self._button)
        if total_buttons == 1:
            b_cols = 1
        elif total_buttons in (3, 6):
            b_cols = 3
        else:
            b_cols = min(b_cols, 2)

        menu = [self._button[i:i + b_cols] for i in range(0, total_buttons, b_cols)]

        # --- Header ---
        if self._header_button:
            h_cnt = len(self._header_button)
            if h_cnt > h_cols:
                header_buttons = [self._header_button[i:i + h_cols] for i in range(0, h_cnt, h_cols)]
                menu = header_buttons + menu
            else:
                menu.insert(0, self._header_button)

        # --- Footer ---
        if self._footer_button:
            f_cnt = len(self._footer_button)
            if f_cnt > f_cols:
                footer_buttons = [self._footer_button[i:i + f_cols] for i in range(0, f_cnt, f_cols)]
                menu.extend(footer_buttons)
            else:
                menu.append(self._footer_button)

        return InlineKeyboardMarkup(menu) if menu else None
