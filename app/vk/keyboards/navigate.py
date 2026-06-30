from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_navigate_keyboard() -> str:
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("Статус", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Куки", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()