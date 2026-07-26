import os
import re
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    PicklePersistence,
    filters,
)


# =========================================================
# 기본 설정
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.getenv("PORT", "10000"))


# =========================================================
# 저장 파일 설정
# =========================================================

RENDER_DATA_DIR = Path("/var/data")

if RENDER_DATA_DIR.exists():
    DATA_FILE = RENDER_DATA_DIR / "missing_report_bot.pkl"
else:
    DATA_FILE = Path("missing_report_bot.pkl")


logger.info(
    "보고 기록 저장 위치: %s",
    DATA_FILE,
)


# =========================================================
# 허용 사용자 설정
# =========================================================

ALLOWED_USER_IDS = {
    498546317,
}


def is_allowed(update: Update) -> bool:
    """허용된 사용자만 봇을 사용할 수 있도록 확인합니다."""

    user = update.effective_user

    if user is None:
        return False

    if not ALLOWED_USER_IDS:
        return True

    return user.id in ALLOWED_USER_IDS


# =========================================================
# 전체 명단
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
# =========================================================

PATTERN = re.compile(
    r"선봉/\d+/[가-힣A-Za-z0-9_-]+"
)


# =========================================================
# 누적 보고자 가져오기
# =========================================================

def get_accumulated_reported(
    context: ContextTypes.DEFAULT_TYPE,
) -> set[str]:

    accumulated_reported = context.bot_data.setdefault(
        "reported",
        set(),
    )

    if not isinstance(
        accumulated_reported,
        set,
    ):
        accumulated_reported = set(
            accumulated_reported
        )

        context.bot_data["reported"] = (
            accumulated_reported
        )

    return accumulated_reported


# =========================================================
# 미보고자 정렬
# =========================================================

def member_sort_key(
    item: str,
):
    try:
        _, team, name = item.split(
            "/",
            2,
        )

        return (
            int(team),
            name,
        )

    except (
        ValueError,
        IndexError,
    ):
        return (
            999999,
            item,
        )


# =========================================================
# 미보고자 계산
# =========================================================

def calculate_missing(
    accumulated_reported: set[str],
) -> list[str]:

    return sorted(
        MEMBERS - accumulated_reported,
        key=member_sort_key,
    )


# =========================================================
# 미보고 명단 메시지 작성
# =========================================================

def make_missing_message(
    missing: list[str],
) -> str:

    if not missing:
        return "🎉 전원 보고 완료!"

    result = [
        "[미보고명단]",
    ]

    current_team = None

    for person in missing:

        try:
            _, team, _ = person.split(
                "/",
                2,
            )

        except ValueError:
            result.append(person)
            continue

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

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    # /start를 눌렀을 때만 초기화
    context.bot_data["reported"] = set()

    await message.reply_text(
        "✅ 새로운 보고를 시작합니다.\n\n"
        "보고 내용을 그대로 붙여넣어 주세요.\n\n"
        "여러 번 나누어 보내도 보고자가 계속 누적됩니다.\n"
        "날짜가 바뀌어도 미보고 명단은 그대로 유지됩니다.\n"
        "미보고자가 다음날 보고하면 미보고 명단에서 제거됩니다.\n"
        "봇이 재시작되어도 저장된 보고 기록을 다시 불러옵니다.\n\n"
        "⚠️ /start 를 다시 보내면 기존 누적 기록이 초기화됩니다.\n\n"
        "현재 미보고 명단을 다시 확인하려면 /status 를 보내주세요."
    )

    logger.info(
        "새로운 보고 시작 및 누적 기록 초기화: user_id=%s",
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

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    accumulated_reported = (
        get_accumulated_reported(
            context
        )
    )

    missing = calculate_missing(
        accumulated_reported
    )

    await message.reply_text(
        make_missing_message(
            missing
        )
    )


# =========================================================
# 일반 보고 처리
# =========================================================

async def check(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    text = message.text or ""

    new_reported = set(
        PATTERN.findall(text)
    )

    valid_reported = (
        new_reported
        & MEMBERS
    )

    if not valid_reported:
        await message.reply_text(
            "⚠️ 명단에서 일치하는 보고자를 찾지 못했습니다.\n\n"
            "보고 문구가 아래 형식인지 확인해 주세요.\n"
            "예: 선봉/3/김아린"
        )
        return

    accumulated_reported = (
        get_accumulated_reported(
            context
        )
    )

    already_reported = (
        valid_reported
        & accumulated_reported
    )

    newly_added = (
        valid_reported
        - accumulated_reported
    )

    accumulated_reported.update(
        valid_reported
    )

    context.bot_data["reported"] = (
        accumulated_reported
    )

    missing = calculate_missing(
        accumulated_reported
    )

    missing_message = make_missing_message(
        missing
    )

    if already_reported:

        already_list = sorted(
            already_reported,
            key=member_sort_key,
        )

        already_message = (
            "ℹ️ 이미 보고 완료된 사람이 포함되어 있습니다.\n\n"
            + "\n".join(
                already_list
            )
        )

        if newly_added:

            new_list = sorted(
                newly_added,
                key=member_sort_key,
            )

            new_message = (
                "\n\n✅ 새로 보고 완료\n\n"
                + "\n".join(
                    new_list
                )
            )

        else:
            new_message = ""

        await message.reply_text(
            already_message
            + new_message
            + "\n\n"
            + missing_message
        )

        return

    if newly_added:
        await message.reply_text(
            missing_message
        )
        return

    await message.reply_text(
        missing_message
    )


# =========================================================
# 오류 처리
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):

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

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN 환경변수가 설정되지 않았습니다."
        )

    if not WEBHOOK_URL:
        raise RuntimeError(
            "WEBHOOK_URL 환경변수가 설정되지 않았습니다."
        )

    persistence = PicklePersistence(
        filepath=DATA_FILE,
        update_interval=5,
    )

    base_url = WEBHOOK_URL.rstrip("/")

    webhook_path = "telegram"

    full_webhook_url = (
        f"{base_url}/{webhook_path}"
    )

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(persistence)
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

    logger.info(
        "보고 기록 저장 파일: %s",
        DATA_FILE,
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
