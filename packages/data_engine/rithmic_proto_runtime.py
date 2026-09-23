"""Compile the user's licensed R|Protocol protobuf schemas at runtime.

Nothing from the vendor kit is copied into the QuantPro repository. The deployment
mounts/extracts the licensed kit and this module generates Python bindings into a
throw-away cache directory using the current protobuf compiler.
"""

from pathlib import Path
import shutil
import tempfile

from grpc_tools import protoc

_REQUIRED = (
    "request_login.proto",
    "response_login.proto",
    "request_heartbeat.proto",
    "response_heartbeat.proto",
    "request_front_month_contract.proto",
    "response_front_month_contract.proto",
    "request_market_data_update.proto",
    "response_market_data_update.proto",
    "last_trade.proto",
    "best_bid_offer.proto",
    "order_book.proto",
    "request_depth_by_order_snapshot.proto",
    "response_depth_by_order_snapshot.proto",
    "request_depth_by_order_updates.proto",
    "response_depth_by_order_updates.proto",
    "depth_by_order.proto",
    "request_list_exchange_permissions.proto",
    "response_list_exchange_permissions.proto",
)


def compile_rithmic_protos(kit_dir: Path) -> Path:
    kit_dir = kit_dir.resolve()
    proto_dir = kit_dir / "proto"
    sample_dir = kit_dir / "samples" / "samples.py"
    if not proto_dir.is_dir() or not sample_dir.is_dir():
        raise RuntimeError("Rithmic kit must contain proto/ and samples/samples.py/")
    for name in _REQUIRED:
        if not (proto_dir / name).is_file():
            raise RuntimeError(f"Rithmic kit is missing required schema: {name}")
    if not (sample_dir / "base.proto").is_file():
        raise RuntimeError("Rithmic kit is missing samples/samples.py/base.proto")

    out = Path(tempfile.mkdtemp(prefix="quantpro-rithmic-proto-"))
    staging = out / "src"
    generated = out / "generated"
    staging.mkdir()
    generated.mkdir()
    shutil.copy2(sample_dir / "base.proto", staging / "base.proto")
    for name in _REQUIRED:
        shutil.copy2(proto_dir / name, staging / name)

    args = ["grpc_tools.protoc", f"-I{staging}", f"--python_out={generated}"]
    args.extend(str(staging / name) for name in ("base.proto", *_REQUIRED))
    if protoc.main(args) != 0:
        raise RuntimeError("Failed to compile Rithmic protobuf schemas")
    return generated
