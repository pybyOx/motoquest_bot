def build_answer_text(
        correct_answer: dict,
        point_info: str,
        user_info: str,
) -> str:
    return f"Ответ на точку {point_info} от {user_info}:"\
           f"\nПравильный ответ:"\
           f"\nтип - {correct_answer['type']}, ответ - {correct_answer['text']}"
