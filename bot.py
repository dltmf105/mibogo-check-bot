import os
import re
import json
import asyncio
import logging
import urllib.error
import urllib.parse
import urllib.request

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
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


TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip()
PORT = int(os.getenv("PORT", "10000"))

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "",
).strip().rstrip("/")

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "",
).strip()

KST = ZoneInfo("Asia/Seoul")


# =========================================================
# 허용 사용자
# =========================================================

ALLOWED_USER_IDS = {
    # 여기에 본인 텔레그램 숫자 ID 입력
    # 예:
    # 498546317,
}


def is_allowed(update: Update) -> bool:
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
# 보고 문구 추출
# =========================================================

PATTERN = re.compile(
    r"선봉/\d+/[가-힣A-Za-z0-9_-]+"
)


# =========================================================
# 정렬
# =========================================================

def member_sort_key(item: str):
    try:
        _, team, name = item.split("/", 2)

        return (
            int(team),
            name,
        )

    except (ValueError, IndexError):
        return (
            999999,
            item,
        )


# =========================================================
# 현재 회차
#
# 월요일 + 화요일 = 같은 회차
# 수요일 + 목요일 = 같은 회차
# =========================================================

def get_current_cycle_id() -> str | None:
    now = datetime.now(KST)
    weekday = now.weekday()

    # 월요일
    if weekday == 0:
        monday = now.date()

        return f"MON_TUE_{monday.isoformat()}"

    # 화요일
    # 전날 월요일과 같은 회차
    if weekday == 1:
        monday = (
            now - timedelta(days=1)
        ).date()

        return f"MON_TUE_{monday.isoformat()}"

    # 수요일
    if weekday == 2:
        wednesday = now.date()

        return f"WED_THU_{wednesday.isoformat()}"

    # 목요일
    # 전날 수요일과 같은 회차
    if weekday == 3:
        wednesday = (
            now - timedelta(days=1)
        ).date()

        return f"WED_THU_{wednesday.isoformat()}"

    # 금요일 / 토요일 / 일요일
    return None


# =========================================================
# Supabase REST 요청
# =========================================================

def supabase_request(
    method: str,
    table_and_query: str,
    body=None,
    prefer: str | None = None,
):
    url = (
        f"{SUPABASE_URL}"
        f"/rest/v1/"
        f"{table_and_query}"
    )

    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "missing-report-bot/1.0",
    }

    # 기존 service_role JWT 키만 Bearer 헤더 추가
    # 새 sb_secret_ 키에는 Authorization 헤더를 넣지 않음
    if SUPABASE_KEY.startswith("eyJ"):
        headers["Authorization"] = (
            f"Bearer {SUPABASE_KEY}"
        )

    if prefer:
        headers["Prefer"] = prefer

    encoded_body = None

    if body is not None:
        encoded_body = json.dumps(
            body,
            ensure_ascii=False,
        ).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=encoded_body,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:

            raw = response.read()

            if not raw:
                return None

            return json.loads(
                raw.decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        error_body = (
            exc.read()
            .decode(
                "utf-8",
                errors="replace",
            )
        )

        logger.error(
            "Supabase HTTP 오류 %s: %s",
            exc.code,
            error_body,
        )

        raise

    except urllib.error.URLError as exc:
        logger.error(
            "Supabase 연결 오류: %s",
            exc,
        )

        raise

    except Exception:
        logger.exception(
            "Supabase 요청 중 오류 발생"
        )

        raise


# =========================================================
# 현재 회차 보고자 불러오기
# =========================================================

def load_reported(
    cycle_id: str,
) -> set[str]:

    query = urllib.parse.urlencode(
        {
            "select": "member",
            "cycle_id": f"eq.{cycle_id}",
        }
    )

    result = supabase_request(
        "GET",
        f"reported_members?{query}",
    )

    if result is None:
        return set()

    if not isinstance(result, list):
        raise RuntimeError(
            "Supabase 응답 형식이 올바르지 않습니다."
        )

    reported = set()

    for row in result:

        if not isinstance(row, dict):
            continue

        member = str(
            row.get(
                "member",
                "",
            )
        ).strip()

        if member in MEMBERS:
            reported.add(member)

    return reported


# =========================================================
# 새 보고자 저장
# =========================================================

def add_reported_members(
    cycle_id: str,
    members: set[str],
) -> None:

    if not members:
        return

    rows = [
        {
            "cycle_id": cycle_id,
            "member": member,
        }
        for member in sorted(
            members,
            key=member_sort_key,
        )
    ]

    query = urllib.parse.urlencode(
        {
            "on_conflict": "cycle_id,member",
        }
    )

    supabase_request(
        "POST",
        f"reported_members?{query}",
        body=rows,
        prefer=(
            "resolution=ignore-duplicates,"
            "return=minimal"
        ),
    )


# =========================================================
# 현재 회차 초기화
#
# 오직 /reset에서만 실행
# =========================================================

def delete_current_cycle(
    cycle_id: str,
) -> None:

    query = urllib.parse.urlencode(
        {
            "cycle_id": f"eq.{cycle_id}",
        }
    )

    supabase_request(
        "DELETE",
        f"reported_members?{query}",
        prefer="return=minimal",
    )


# =========================================================
# 미보고자 계산
# =========================================================

def calculate_missing(
    reported: set[str],
) -> list[str]:

    return sorted(
        MEMBERS - reported,
        key=member_sort_key,
    )


# =========================================================
# 미보고 명단 메시지
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
# 사용하지 않는 요일 안내
# =========================================================

async def send_not_active_message(
    message,
):
    await message.reply_text(
        "📌 현재는 보고 집계 사용 요일이 아닙니다.\n\n"
        "월요일 → 화요일\n"
        "수요일 → 목요일\n\n"
        "위 회차에서 사용해 주세요."
    )


# =========================================================
# /start
#
# 초기화하지 않음
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

    cycle_id = get_current_cycle_id()

    if cycle_id is None:
        await send_not_active_message(
            message
        )
        return

    try:
        reported = await asyncio.to_thread(
            load_reported,
            cycle_id,
        )

    except Exception:
        await message.reply_text(
            "⚠️ 저장된 보고 기록을 불러오는 중 오류가 발생했습니다."
        )
        return

    missing = calculate_missing(
        reported
    )

    await message.reply_text(
        "✅ 미보고 확인봇이 실행 중입니다.\n\n"
        "보고 내용을 그대로 붙여넣어 주세요.\n\n"
        "월요일과 화요일은 같은 보고 회차입니다.\n"
        "수요일과 목요일은 같은 보고 회차입니다.\n"
        "화요일과 목요일에는 기록이 초기화되지 않습니다.\n\n"
        "📌 /status : 현재 미보고 명단 확인\n"
        "📌 /reset : 현재 회차 기록 초기화\n\n"
        + make_missing_message(
            missing
        )
    )


# =========================================================
# /status
#
# 초기화하지 않음
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

    cycle_id = get_current_cycle_id()

    if cycle_id is None:
        await send_not_active_message(
            message
        )
        return

    try:
        reported = await asyncio.to_thread(
            load_reported,
            cycle_id,
        )

    except Exception:
        await message.reply_text(
            "⚠️ 저장된 보고 기록을 불러오는 중 오류가 발생했습니다."
        )
        return

    missing = calculate_missing(
        reported
    )

    await message.reply_text(
        make_missing_message(
            missing
        )
    )


# =========================================================
# /reset
#
# 이 명령을 직접 보낼 때만 초기화
# =========================================================

async def reset(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not is_allowed(update):
        return

    message = update.effective_message

    if message is None:
        return

    cycle_id = get_current_cycle_id()

    if cycle_id is None:
        await send_not_active_message(
            message
        )
        return

    try:
        await asyncio.to_thread(
            delete_current_cycle,
            cycle_id,
        )

    except Exception:
        await message.reply_text(
            "⚠️ 보고 기록 초기화 중 오류가 발생했습니다."
        )
        return

    await message.reply_text(
        "♻️ 현재 회차 기록을 모두 초기화했습니다.\n"
        "전체 명단에서 새로 집계를 시작합니다."
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

    cycle_id = get_current_cycle_id()

    if cycle_id is None:
        await send_not_active_message(
            message
        )
        return

    text = message.text or ""

    found_reported = {
        item.strip()
        for item in PATTERN.findall(text)
    }

    valid_reported = (
        found_reported
        & MEMBERS
    )

    if not valid_reported:
        await message.reply_text(
            "⚠️ 명단에서 일치하는 보고자를 찾지 못했습니다.\n\n"
            "보고 문구가 아래 형식인지 확인해 주세요.\n"
            "예: 선봉/3/김아린"
        )
        return

    # 현재 회차의 기존 보고자 조회
    try:
        accumulated_reported = (
            await asyncio.to_thread(
                load_reported,
                cycle_id,
            )
        )

    except Exception:
        await message.reply_text(
            "⚠️ 기존 보고 기록을 불러오는 중 오류가 발생했습니다."
        )
        return

    already_reported = (
        valid_reported
        & accumulated_reported
    )

    newly_added = (
        valid_reported
        - accumulated_reported
    )

    # 새 보고자만 저장
    if newly_added:
        try:
            await asyncio.to_thread(
                add_reported_members,
                cycle_id,
                newly_added,
            )

        except Exception:
            await message.reply_text(
                "⚠️ 보고 기록 저장 중 오류가 발생했습니다."
            )
            return

    # 저장 후 DB 상태 다시 조회
    try:
        updated_reported = (
            await asyncio.to_thread(
                load_reported,
                cycle_id,
            )
        )

    except Exception:
        await message.reply_text(
            "⚠️ 저장된 보고 기록을 다시 확인하는 중 오류가 발생했습니다."
        )
        return

    missing = calculate_missing(
        updated_reported
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

    if context.error:
        logger.error(
            "텔레그램 업데이트 처리 중 오류 발생",
            exc_info=(
                type(context.error),
                context.error,
                context.error.__traceback__,
            ),
        )


# =========================================================
# 환경변수 검사
# =========================================================

def validate_environment() -> None:

    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN 환경변수가 설정되지 않았습니다."
        )

    if not WEBHOOK_URL:
        raise RuntimeError(
            "WEBHOOK_URL 환경변수가 설정되지 않았습니다."
        )

    if not SUPABASE_URL:
        raise RuntimeError(
            "SUPABASE_URL 환경변수가 설정되지 않았습니다."
        )

    if not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_KEY 환경변수가 설정되지 않았습니다."
        )

    if not SUPABASE_URL.startswith("https://"):
        raise RuntimeError(
            "SUPABASE_URL은 https://로 시작해야 합니다."
        )

    if "/rest/v1" in SUPABASE_URL:
        raise RuntimeError(
            "SUPABASE_URL에는 /rest/v1을 넣으면 안 됩니다."
        )

    if not (
        SUPABASE_KEY.startswith("sb_secret_")
        or SUPABASE_KEY.startswith("eyJ")
    ):
        raise RuntimeError(
            "SUPABASE_KEY에는 sb_secret_ 키 또는 "
            "service_role 키를 입력해야 합니다."
        )


# =========================================================
# 봇 실행
# =========================================================

def main():

    validate_environment()

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
            "status",
            status,
        )
    )

    app.add_handler(
        CommandHandler(
            "reset",
            reset,
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
