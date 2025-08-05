from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["test"])


@router.get("")
def hello_world():
    return "Hello World!"
