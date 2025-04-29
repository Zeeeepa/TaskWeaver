import json
from typing import Any, Callable, List, Optional

from standalone_taskweaver.memory import Attachment, Post
from standalone_taskweaver.memory.attachment import AttachmentType
from standalone_taskweaver.module.event_emitter import PostEventProxy


class PostTranslator:
    """
    PostTranslator is used to translate between raw text and post.
    """

    def post_to_raw_text(
        self,
        post: Post,
        content_formatter: Optional[Callable[[Attachment], str]] = None,
        if_format_message: bool = True,
        if_format_send_to: bool = True,
        ignored_types: Optional[List[AttachmentType]] = None,
    ) -> str:
        """
        Convert a post to raw text.
        :param post: The post.
        :param content_formatter: The content formatter.
        :param if_format_message: Whether to format the message.
        :param if_format_send_to: Whether to format the send_to field.
        :param ignored_types: The ignored attachment types.
        :return: The raw text.
        """
        if ignored_types is None:
            ignored_types = []

        raw_text = ""
        if if_format_message and post.message:
            raw_text += f"{post.message}\\n\\n"

        for attachment in post.attachment_list:
            if attachment.type in ignored_types:
                continue
            if content_formatter is not None:
                raw_text += f"{content_formatter(attachment)}\\n\\n"
            else:
                raw_text += f"{attachment.content}\\n\\n"

        if if_format_send_to:
            raw_text += f"send_to: {post.send_to}"

        return raw_text

    def raw_text_to_post(
        self,
        post_proxy: PostEventProxy,
        llm_output: Any,
        validation_func: Optional[Callable[[Post], None]] = None,
        early_stop: Optional[Callable[[AttachmentType, str], bool]] = None,
    ) -> None:
        """
        Convert raw text to a post.
        :param post_proxy: The post proxy.
        :param llm_output: The LLM output.
        :param validation_func: The validation function.
        :param early_stop: The early stop function.
        """
        try:
            # parse the LLM output as JSON
            llm_output_str = ""
            for chunk in llm_output:
                llm_output_str += chunk["content"]
                try:
                    response = json.loads(llm_output_str)
                    if "response" in response:
                        response = response["response"]
                        if "send_to" in response:
                            post_proxy.update_send_to(response["send_to"])
                        if "message" in response:
                            post_proxy.update_message(response["message"])
                        if "thought" in response:
                            post_proxy.update_attachment(
                                response["thought"],
                                AttachmentType.thought,
                            )
                        if "reply_type" in response:
                            post_proxy.update_attachment(
                                response["reply_type"],
                                AttachmentType.reply_type,
                            )
                        if "reply_content" in response:
                            post_proxy.update_attachment(
                                response["reply_content"],
                                AttachmentType.reply_content,
                            )
                            if early_stop is not None and early_stop(
                                AttachmentType.reply_content,
                                response["reply_content"],
                            ):
                                break
                        if "init_plan" in response:
                            post_proxy.update_attachment(
                                response["init_plan"],
                                AttachmentType.init_plan,
                            )
                        if "plan" in response:
                            post_proxy.update_attachment(
                                response["plan"],
                                AttachmentType.plan,
                            )
                        if "current_plan_step" in response:
                            post_proxy.update_attachment(
                                response["current_plan_step"],
                                AttachmentType.current_plan_step,
                            )
                except json.JSONDecodeError:
                    pass

            if validation_func is not None:
                validation_func(post_proxy.post)
        except Exception as e:
            post_proxy.error(f"Failed to parse LLM output: {e}")

