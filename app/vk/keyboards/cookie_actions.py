from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_cookie_actions_keyboard(cookie_file_exists: bool = True) -> str:
    keyboard = VkKeyboard(one_time=False)
    
    keyboard.add_button("Установить куки", color=VkKeyboardColor.PRIMARY)
    if cookie_file_exists:
        keyboard.add_button("Текущие куки", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button("Главная", color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()