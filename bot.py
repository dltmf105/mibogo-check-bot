import os
import re
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# Render 환경변수
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://mibogo-check-bot.onrender.com"
)

ALLOWED_USER_ID_TEXT = os.getenv(
    "ALLOWED_USER_ID",
    "498546317"
)

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)


# 로그 설정
logging.basicConfig(
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# 허용 사용자 ID
try:
    ALLOWED_USER_ID = int(
        ALLOWED_USER_ID_TEXT
    )
except ValueError as error:
    raise RuntimeError(
        "ALLOWED_USER_ID는 숫자여야 합니다."
    ) from error


# 전체 명단
MEMBERS = {
    "선봉/1/김수연3",
    "선봉/1/기형진",
    "선봉/1/김애림",
    "선봉/1/정수철",
    "선봉/1/김다원2",
    "선봉/1/김민영",
    "선봉/1/김상용",
    "선봉/1/김은비2",
    "선봉/1/김지호",
    "선봉/1/김희주",
    "선봉/1/나찬민",
    "선봉/1/서상국",
    "선봉/1/심재원",
    "선봉/1/오승욱",
    "선봉/1/유정현",
    "선봉/1/이가영2",
    "선봉/1/이인영",
    "선봉/1/임혜정",
    "선봉/1/장민혁",
    "선봉/1/장희원",
    "선봉/1/정가은",
    "선봉/1/조서희",
    "선봉/1/조원진",
    "선봉/1/조은서",
    "선봉/1/최지나",
    "선봉/1/하세린",
    "선봉/1/한수연2",

    "선봉/2/남완전",
    "선봉/2/김이슬",
    "선봉/2/박효범",
    "선봉/2/김명재",
    "선봉/2/김미정",
    "선봉/2/김연우",
    "선봉/2/김유찬",
    "선봉/2/김채윤",
    "선봉/2/김희원",
    "선봉/2/나연균",
    "선봉/2/노제나",
    "선봉/2/문철균",
    "선봉/2/박세진",
    "선봉/2/서시온",
    "선봉/2/윤소영",
    "선봉/2/윤주혜",
    "선봉/2/이람희",
    "선봉/2/이사민",
    "선봉/2/이유진3",
    "선봉/2/이지영",
    "선봉/2/정서",
    "선봉/2/정유빈",
    "선봉/2/정은진",
    "선봉/2/정주호",
    "선봉/2/최건우",
    "선봉/2/한슬비",

    "선봉/3/나다은",
    "선봉/3/김연지",
    "선봉/3/이덕희",
    "선봉/3/박민혁",
    "선봉/3/곽혜진",
    "선봉/3/이상민",
    "선봉/3/심지수",
    "선봉/3/김은혜1",
    "선봉/3/김세연",
    "선봉/3/김성주",
    "선봉/3/나보라",
    "선봉/3/한헌영",
    "선봉/3/곽혜미",
    "선봉/3/반진후",
    "선봉/3/김아린",
    "선봉/3/이소평",
    "선봉/3/최아선",
    "선봉/3/정현1",
    "선봉/3/강수빈",
    "선봉/3/이태현",
    "선봉/3/이혜연",
    "선봉/3/이은혜",
    "선봉/3/송예주",
    "선봉/3/임장혁",
    "선봉/3/최세란",
    "선봉/3/황소윤",
    "선봉/3/유하은",

    "선봉/4/문성준",
    "선봉/4/조의연",
    "선봉/4/문소원",
    "선봉/4/오민석",
    "선봉/4/이규일",
    "선봉/4/강경호",
    "선봉/4/김남수",
    "선봉/4/김다운",
    "선봉/4/김선우1",
    "선봉/4/김세령",
    "선봉/4/김주영",
    "선봉/4/김지운",
    "선봉/4/김호성",
    "선봉/4/명윤성",
    "선봉/4/박준석",
    "선봉/4/박찬우",
    "선봉/4/범순철",
    "선봉/4/오세열",
    "선봉/4/윤상준",
    "선봉/4/이정인",
    "선봉/4/이해성",
    "선봉/4/임홍열",
    "선봉/4/전덕성",
    "선봉/4/정우혁",
    "선봉/4/정초은",
    "선봉/4/조찬익",
    "선봉/4/최미나",
    "선봉/4/최서경",
    "선봉/4/한대준",
    "선봉/4/홍지석",
}


# 보고 문구 추출 정규식
PATTERN = re.compile(
    r"선봉/\d+/[^\s/]+"
)


def is_allowed(
    update: Update
) -> bool:
    """허용된 사용자만 봇을 사용하게 합니다."""

    if update.effective_user is None:
        return False

    return (
        update.effective_user.id
        == ALLOWED_USER_ID
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """봇 시작 안내."""

    if not is_allowed(update):
        return

    if update.message is None:
        return

    await update.message.reply_text(
        "보고 내용을 그대로 붙여넣어 주세요.\n\n"
        "여러 번 나누어 보내도 보고자가 계속 누적됩니다.\n"
        "새로운 보고를 시작할 때는 /reset 을 보내주세요."
    )


async def reset(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """누적 보고 기록 초기화."""

    if not is_allowed(update):
        return

    if update.message is None:
        return

    context.user_data["reported"] = set()

    await update.message.reply_text(
        "✅ 누적 보고 기록을 초기화했습니다.\n"
        "새로운 보고를 붙여넣어 주세요."
    )


async def check(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """보고 내용을 확인하고 미보고 명단을 출력합니다."""

    if not is_allowed(update):
        return

    if update.message is None:
        return

    text = update.message.text or ""

    # 이번 메시지에서 보고된 사람 추출
    new_reported = set(
        PATTERN.findall(text)
    )

    # 전체 명단에 실제로 있는 사람만 인정
    valid_reported = (
        new_reported
        & MEMBERS
    )

    # 누적 보고 기록
    accumulated_reported = (
        context.user_data.setdefault(
            "reported",
            set()
        )
    )

    # 이번 보고자를 누적 기록에 추가
    accumulated_reported.update(
        valid_reported
    )

    # 미보고자 계산
    missing = sorted(
        MEMBERS
        - accumulated_reported,
        key=lambda item: (
            int(
                item.split("/")[1]
            ),
            item.split("/")[2],
        ),
    )

    # 전원 보고 완료
    if not missing:
        await update.message.reply_text(
            "🎉 전원 보고 완료!"
        )
        return

    # 미보고 명단 작성
    result = [
        "[미보고명단]"
    ]

    current_team = None

    for person in missing:
        _, team, _ = person.split(
            "/",
            2
        )

        if current_team != team:
            current_team = team
            result.append(
                f"\n{team}구역"
            )

        result.append(person)

    await update.message.reply_text(
        "\n".join(result)
    )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    """오류를 Render 로그에 출력합니다."""

    logger.exception(
        "텔레그램 업데이트 처리 중 오류 발생",
        exc_info=context.error,
    )


def main():
    """웹훅 방식으로 봇을 실행합니다."""

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN 환경변수가 설정되지 않았습니다."
        )

    if not WEBHOOK_URL:
        raise RuntimeError(
            "WEBHOOK_URL 환경변수가 설정되지 않았습니다."
        )

    # 주소 끝의 / 제거
    base_url = WEBHOOK_URL.rstrip("/")

    webhook_path = "telegram"

    full_webhook_url = (
        f"{base_url}/{webhook_path}"
    )

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "reset",
            reset
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            check
        )
    )

    app.add_error_handler(
        error_handler
    )

    logger.info(
        "미보고 확인봇 웹훅 실행 시작"
    )

    logger.info(
        "Webhook URL: %s",
        full_webhook_url
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=full_webhook_url,

        # Render에서는 외부 HTTPS를 사용하지만
        # 내부 서버는 HTTP로 실행합니다.
        cert=None,
        key=None,

        # 배포 전에 쌓인 오래된 메시지를 제거합니다.
        drop_pending_updates=True,

        # 정상 종료 신호를 처리합니다.
        close_loop=True,
        stop_signals=None,
    )


if __name__ == "__main__":
    main()
