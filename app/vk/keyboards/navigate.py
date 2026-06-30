from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_navigate_keyboard() -> str:
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("Статус", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Помощь", color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()

    keyboard.add_button("Загрузить GPX", color=VkKeyboardColor.POSITIVE)

    return keyboard.get_keyboard()