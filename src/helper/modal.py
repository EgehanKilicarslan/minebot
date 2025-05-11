from typing import Callable

import hikari
from lightbulb.components.modals import Modal, TextInput

from model.schemas import BaseTextInput


class ModalHelper:
    @staticmethod
    def get_field(
        instance: Modal, key: BaseTextInput, min_lenght: int = 0, max_length: int = 4000
    ) -> TextInput:
        mapper: dict[str, Callable] = {
            "SHORT": instance.add_short_text_input,
            "PARAGRAPH": instance.add_paragraph_text_input,
        }

        return mapper[key.style](
            label=key.label,
            placeholder=key.placeholder or hikari.UNDEFINED,
            value=key.value or hikari.UNDEFINED,
            min_length=min_lenght,
            max_length=max_length,
        )
