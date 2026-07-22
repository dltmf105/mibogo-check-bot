import logging
import os
import re

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# =========================================================
# Render 환경변수
# =========================================================

TOKEN = os.getenv("BOT_TOKEN", "").strip()

WEBHOOK_URL = os.getenv(
    "WEBHOOK_URL",
    "https://mibogo-check-bot.onrender.com",
).strip()

ALLOWED_USER_ID_TEXT = os.getenv(
    "ALLOWED_USER_ID",
    "498546317",
).strip()

PORT = int(
    os.getenv(
        "PORT",
        "10000",
    )
)


# =========================================================
# 로그 설정
# =========================================================

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


# =========================================================
# 허용 사용자 ID
# =========================================================

try:
    ALLOWED_USER_ID = int(
        ALLOWED_USER_ID_TEXT
    )
except ValueError as error:
    raise RuntimeError(
        "ALLOWED_USER_ID는 숫자여야 합니다."
    ) from error


# =========================================================
# 전체 명단
#
# 아래 MEMBERS에는 현재 사용 중인 명단을
# 그대로 넣으면 됩니다.
# =========================================================

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


# =========================================================
# 보고 문구 추출 정규식
#
# 예:
# 선봉/3/김아린
# 선봉/1/김수연3
# =========================================================

PATTERN = re.compile(
    r"선봉/\d+/[^\s/]+"
)


# =========================================================
# 허용 사용자 확인
# =========================================================

def is_allowed(
    update: Update,
) -> bool:
    """허용된 사용자만 봇을 사용할 수 있게 합니다."""

    user = update.effective_user

    if user is None:
        return False

    return user.id == ALLOWED_USER_ID


# =========================================================
# 미보고자 계산
# =========================================================

def calculate_missing(
    accumulated_reported: set[str],
) -> list[str]:
    """누적 보고자 목록을 기준으로 미보고자를 계산합니다."""

    return sorted(
        MEMBERS - accumulated_reported,
        key=lambda item: (
            int(item.split("/", 2)[1]),
            item.split("/", 2)[2],
        ),
    )


# =========================================================
# 미보고 명단 메시지 작성
# =========================================================

def make_missing_message(
    missing: list[str],
) -> str:
    """미보고자 목록을 메시지 문자열로 만듭니다."""

    if not missing:
        return "🎉 전원 보고 완료!"

    result = [
        "[미보고명단]",
    ]

    current_team = None

    for person in missing:
        _, team, _ = person.split(
            "/",
            2,
        )

        if current_team != team:
            current_team = team

            result.append(
                f"\n{team}구역"
            )

        result.append(person)

    return "\n".join(result)


# =========================================================
# /start
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """봇 시작 안내."""

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    await message.reply_text(
        "보고 내용을 그대로 붙여넣어 주세요.\n\n"
        "여러 번 나누어 보내도 보고자가 계속 누적됩니다.\n"
        "시간이 지난 뒤 새 보고를 보내도 이어서 반영됩니다.\n\n"
        "새로운 보고를 시작할 때는 /reset 을 보내주세요.\n"
        "현재 미보고 명단을 다시 확인하려면 /status 를 보내주세요."
    )


# =========================================================
# /reset
# =========================================================

async def reset(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """누적 보고 기록 초기화."""

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    context.user_data["reported"] = set()

    await message.reply_text(
        "✅ 누적 보고 기록을 초기화했습니다.\n"
        "새로운 보고를 붙여넣어 주세요."
    )

    logger.info(
        "누적 보고 기록 초기화: user_id=%s",
        update.effective_user.id
        if update.effective_user
        else None,
    )


# =========================================================
# /status
# =========================================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """현재까지 누적된 내용을 기준으로 미보고 명단을 출력합니다."""

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    accumulated_reported = context.user_data.setdefault(
        "reported",
        set(),
    )

    missing = calculate_missing(
        accumulated_reported
    )

    await message.reply_text(
        make_missing_message(missing)
    )


# =========================================================
# 일반 보고 처리
# =========================================================

async def check(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """보고 내용을 누적하고 최신 미보고 명단을 출력합니다."""

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    text = message.text or ""

    logger.info(
        "보고 메시지 수신: user_id=%s, update_id=%s, text=%r",
        update.effective_user.id
        if update.effective_user
        else None,
        update.update_id,
        text[:300],
    )

    # 이번 메시지에서 보고 문구 추출
    new_reported = set(
        PATTERN.findall(text)
    )

    logger.info(
        "정규식 추출 결과: %s",
        sorted(new_reported),
    )

    # 전체 명단에 실제로 존재하는 보고자만 인정
    valid_reported = (
        new_reported
        & MEMBERS
    )

    logger.info(
        "유효 보고자: %s",
        sorted(valid_reported),
    )

    # 명단과 일치하는 보고자가 없는 경우
    if not valid_reported:
        await message.reply_text(
            "⚠️ 명단에서 일치하는 보고자를 찾지 못했습니다.\n\n"
            "보고 문구가 아래 형식인지 확인해 주세요.\n"
            "예: 선봉/3/김아린"
        )
        return

    # 기존 누적 보고 기록
    accumulated_reported = context.user_data.setdefault(
        "reported",
        set(),
    )

    # 이번 메시지에서 새로 추가되는 사람
    newly_added = (
        valid_reported
        - accumulated_reported
    )

    # 기존 기록에 누적
    accumulated_reported.update(
        valid_reported
    )

    logger.info(
        "새로 추가된 보고자: %s",
        sorted(newly_added),
    )

    logger.info(
        "현재 누적 보고자 수: %s",
        len(accumulated_reported),
    )
# 최신 미보고자 계산
missing = calculate_missing(
    accumulated_reported
)
    # 이번 메시지에 새로 반영된 사람이 없는 경우
    if not newly_added:
        await message.reply_text(
            "ℹ️ 이미 반영된 보고입니다.\n\n"
            + make_missing_message(missing)
        )
        return

    # 새로운 보고가 있으면 안내 문장 없이 미보고 명단만 출력
    await message.reply_text(
        make_missing_message(missing)
    )


# =========================================================
# 오류 처리
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    """오류를 Render 로그에 출력합니다."""

    logger.error(
        "텔레그램 업데이트 처리 중 오류 발생",
        exc_info=(
            type(context.error),
            context.error,
            context.error.__traceback__,
        )
        if context.error
        else None,
    )


# =========================================================
# 봇 실행
# =========================================================

def main():
    """Render에서 웹훅 방식으로 봇을 실행합니다."""

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN 환경변수가 설정되지 않았습니다."
        )

    if not WEBHOOK_URL:
        raise RuntimeError(
            "WEBHOOK_URL 환경변수가 설정되지 않았습니다."
        )

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
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "reset",
            reset,
        )
    )

    app.add_handler(
        CommandHandler(
            "status",
            status,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            check,
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
        full_webhook_url,
    )

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=webhook_path,
        webhook_url=full_webhook_url,
        cert=None,
        key=None,
        drop_pending_updates=False,
        allowed_updates=[
            "message",
        ],
        close_loop=True,
        stop_signals=None,
    )


if __name__ == "__main__":
    main()
