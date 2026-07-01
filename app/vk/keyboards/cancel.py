from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_cancel_keyboard() -> str:
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()