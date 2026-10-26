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
# 허용 사용자 설정
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
    "창조/1/최아선",
    "창조/1/김세연",
    "창조/1/나다은",
    "창조/1/강수빈",
    "창조/1/곽혜미",
    "창조/1/곽혜진",
    "창조/1/김성주",
    "창조/1/김아린",
    "창조/1/김연지",
    "창조/1/김은혜1",
    "창조/1/나보라",
    "창조/1/박민혁",
    "창조/1/반진후",
    "창조/1/송예주",
    "창조/1/심지수",
    "창조/1/유하은",
    "창조/1/이덕희",
    "창조/1/이상민",
    "창조/1/이소평",
    "창조/1/이은혜",
    "창조/1/이태현",
    "창조/1/이혜연",
    "창조/1/임장혁",
    "창조/1/정우혁",
    "창조/1/정현1",
    "창조/1/최미나",
    "창조/1/최서경",
    "창조/1/최세란",
    "창조/1/한헌영",
    "창조/1/황소윤",
    "창조/1/김영재",

    "창조/2/남완전",
    "창조/2/김이슬",
    "창조/2/박효범",
    "창조/2/오민석",
    "창조/2/김명재",
    "창조/2/김미정",
    "창조/2/김연우",
    "창조/2/김유찬",
    "창조/2/김채윤",
    "창조/2/김희원",
    "창조/2/나연균",
    "창조/2/노제나",
    "창조/2/명윤성",
    "창조/2/문철균",
    "창조/2/박세진",
    "창조/2/서시온",
    "창조/2/윤소영",
    "창조/2/윤주혜",
    "창조/2/이람희",
    "창조/2/이사민",
    "창조/2/이유진3",
    "창조/2/이지영",
    "창조/2/전영훈",
    "창조/2/정서",
    "창조/2/정유빈",
    "창조/2/정은진",
    "창조/2/정주호",
    "창조/2/조찬익",
    "창조/2/최건우",
    "창조/2/한슬비",

    "창조/3/김수연3",
    "창조/3/기형진",
    "창조/3/김애림",
    "창조/3/정수철",
    "창조/3/김다원2",
    "창조/3/김민영",
    "창조/3/김상용",
    "창조/3/김은비2",
    "창조/3/김의령",
    "창조/3/김지호",
    "창조/3/김희주",
    "창조/3/나찬민",
    "창조/3/서상국",
    "창조/3/심재원",
    "창조/3/염재원",
    "창조/3/오승욱",
    "창조/3/오현주",
    "창조/3/유정현",
    "창조/3/이가영2",
    "창조/3/이인영",
    "창조/3/임혜정",
    "창조/3/장민혁",
    "창조/3/장희원",
    "창조/3/정가은",
    "창조/3/조서희",
    "창조/3/조원진",
    "창조/3/조은서",
    "창조/3/최지나",
    "창조/3/하세린",
    "창조/3/한수연2",
    "창조/3/지정우",

    "창조/4/허유림",
    "창조/4/박재연",
    "창조/4/배은빈",
    "창조/4/국혜진",
    "창조/4/김도연1",
    "창조/4/김민지2",
    "창조/4/김서진",
    "창조/4/김수현1",
    "창조/4/김순민",
    "창조/4/김연지2",
    "창조/4/박다혜",
    "창조/4/박시은1",
    "창조/4/서예린",
    "창조/4/양은우",
    "창조/4/용명우",
    "창조/4/유지은",
    "창조/4/윤나름",
    "창조/4/이덕주",
    "창조/4/이상철",
    "창조/4/이수민2",
    "창조/4/정두리",
    "창조/4/정수",
    "창조/4/정애리",
    "창조/4/정현주2",
    "창조/4/정효섭",
    "창조/4/조홍길",
    "창조/4/최수호",
    "창조/4/최인영",
    "창조/4/최현준",
    "창조/4/황민수",
    "창조/4/이지수",

    "창조/5/김수화",
    "창조/5/문소원",
    "창조/5/고은지",
    "창조/5/김세령",
    "창조/5/김유권",
    "창조/5/김주연",
    "창조/5/김하늘",
    "창조/5/김형준1",
    "창조/5/박유찬",
    "창조/5/박찬우",
    "창조/5/박평화",
    "창조/5/범순철",
    "창조/5/신정민",
    "창조/5/이정인",
    "창조/5/이주미",
    "창조/5/장아원",
    "창조/5/장은혜",
    "창조/5/장혜진",
    "창조/5/전덕성",
    "창조/5/정승민1",
    "창조/5/조강산",
    "창조/5/조강수",
    "창조/5/채기영",
    "창조/5/홍은혜",
    "창조/5/홍지석",
    "창조/5/김남수",
    "창조/5/유은섭",

    "창조/6/최보선",
    "창조/6/손주연",
    "창조/6/이규일",
    "창조/6/강경호",
    "창조/6/고영건",
    "창조/6/김다운",
    "창조/6/김선우1",
    "창조/6/김예림",
    "창조/6/김은설",
    "창조/6/김종원",
    "창조/6/김주영",
    "창조/6/김지운",
    "창조/6/김창민",
    "창조/6/김호성",
    "창조/6/서은수",
    "창조/6/오세열",
    "창조/6/윤상준",
    "창조/6/이다혜",
    "창조/6/이명아",
    "창조/6/이해성",
    "창조/6/정초은",
    "창조/6/정한서",
    "창조/6/조은서1",
    "창조/6/조의연",
    "창조/6/한대준",
    "창조/6/황도진",
    "창조/6/임홍열",
}


# =========================================================
# 보고 문구 추출 정규식
# =========================================================

PATTERN = re.compile(
    r"창조/\d+/[가-힣A-Za-z0-9_-]+"
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
# 일요일 + 월요일 = 같은 회차
# 수요일 + 목요일 = 같은 회차
#
# Python weekday()
# 월=0 / 화=1 / 수=2 / 목=3 / 금=4 / 토=5 / 일=6
# =========================================================

def get_current_cycle_id() -> str | None:
    now = datetime.now(KST)
    weekday = now.weekday()

    # 일요일: 새 일·월 회차 시작
    if weekday == 6:
        sunday = now.date()

        return f"SUN_MON_{sunday.isoformat()}"

    # 월요일: 전날 일요일과 동일한 회차
    if weekday == 0:
        sunday = (
            now - timedelta(days=1)
        ).date()

        return f"SUN_MON_{sunday.isoformat()}"

    # 수요일: 새 수·목 회차 시작
    if weekday == 2:
        wednesday = now.date()

        return f"WED_THU_{wednesday.isoformat()}"

    # 목요일: 전날 수요일과 동일한 회차
    if weekday == 3:
        wednesday = (
            now - timedelta(days=1)
        ).date()

        return f"WED_THU_{wednesday.isoformat()}"

    # 화요일 / 금요일 / 토요일
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

    # 기존 eyJ 형태의 service_role 키 사용 시
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
# 오직 /reset에서만 호출
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
# 집계하지 않는 요일 안내
# =========================================================

async def send_not_active_message(
    message,
):
    await message.reply_text(
        "📌 오늘은 보고 집계일이 아닙니다.\n\n"
        "보고 집계는 아래 요일에만 가능합니다.\n\n"
        "일요일 · 월요일\n"
        "수요일 · 목요일"
    )


# =========================================================
# /start
#
# 안내문과 미보고 명단을 별도 메시지로 전송
# 초기화 기능 없음
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

    # 첫 번째 메시지: 안내문
    await message.reply_text(
        "✅ 미보고 확인봇이 실행 중입니다.\n\n"
        "보고 내용을 그대로 붙여넣어 주세요.\n\n"
        "일요일과 월요일은 같은 보고 회차입니다.\n"
        "수요일과 목요일은 같은 보고 회차입니다.\n"
        "월요일과 목요일에는 앞날의 기록이 그대로 유지됩니다.\n\n"
        "📌 /status : 현재 미보고 명단 확인\n"
        "📌 /reset : 현재 회차 기록 초기화"
    )

    # 두 번째 메시지: 미보고 명단
    await message.reply_text(
        make_missing_message(
            missing
        )
    )


# =========================================================
# /status
#
# 현재 미보고 명단만 전송
# 초기화 기능 없음
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
# 직접 명령했을 때만 현재 회차 초기화
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

    # 화요일 / 금요일 / 토요일에는 보고 처리 안 함
    if cycle_id is None:
        await send_not_active_message(
            message
        )
        return

    text = message.text or ""

    found_reported = {
        item.strip()
        for item in PATTERN.findall(
            text
        )
    }

    valid_reported = (
        found_reported
        & MEMBERS
    )

    # 명단과 일치하지 않는 이름을 따로 찾음
    invalid_reported = (
        found_reported
        - MEMBERS
    )

    # 명단과 일치하지 않는 이름이 있으면 안내
    if invalid_reported:
        invalid_list = sorted(
            invalid_reported,
            key=member_sort_key,
        )

        await message.reply_text(
            "⚠️ 양식 틀린 사람\n\n"
            + "\n".join(invalid_list)
        )

    # 정상 보고자가 없는 경우 잘못된 명단만 알리고 종료
    if not valid_reported:
        if not invalid_reported:
            await message.reply_text(
                "⚠️ 명단에서 일치하는 보고자를 찾지 못했습니다.\n\n"
                "보고 문구가 아래 형식인지 확인해 주세요.\n"
                "예: 창조/1/김아린"
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

    # 새 보고자만 Supabase에 추가
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

    # 저장 후 실제 DB 상태 다시 조회
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

    # 이미 보고한 사람이 포함된 경우
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

        # 안내 메시지와 미보고 명단 따로 전송
        await message.reply_text(
            already_message
            + new_message
        )

        await message.reply_text(
            missing_message
        )

        return

    # 전부 새로운 보고자라면 미보고 명단만 전송
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
# 환경변수 확인
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

    if not SUPABASE_URL.startswith(
        "https://"
    ):
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
