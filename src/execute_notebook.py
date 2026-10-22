"""Execute a self-contained notebook and persist its outputs without Jupyter server packages.

Used for the submitted audit notebook because this project intentionally does not depend on
nbclient/ipykernel. It executes code cells in one Python namespace and writes standard notebook
outputs; execution stops and records a traceback at the first failing cell.
"""

import base64
import contextlib
import io
import sys
import traceback
import uuid
from pathlib import Path

import nbformat


def _text_output(text: str):
    return nbformat.v4.new_output("stream", name="stdout", text=text)


def execute(path: Path) -> None:
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        cell.setdefault("id", uuid.uuid4().hex[:8])
    namespace = {"__name__": "__main__"}
    current_outputs = []

    def display(*values, **_kwargs):
        for value in values:
            data = {"text/plain": repr(value)}
            if hasattr(value, "to_html"):
                data["text/html"] = value.to_html()
            current_outputs.append(nbformat.v4.new_output("execute_result", data=data, execution_count=execution_count))

    namespace["display"] = display
    execution_count = 0
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        execution_count += 1
        cell.execution_count = execution_count
        current_outputs = []
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                exec(compile(cell.source, f"{path}:cell-{execution_count}", "exec"), namespace)
            if "plt" in namespace:
                plt = namespace["plt"]
                figures = [plt.figure(number) for number in plt.get_fignums()]
                for figure in figures:
                    image = io.BytesIO()
                    figure.savefig(image, format="png", bbox_inches="tight")
                    current_outputs.append(nbformat.v4.new_output(
                        "display_data", data={"image/png": base64.b64encode(image.getvalue()).decode("ascii"), "text/plain": "Matplotlib figure"}
                    ))
                plt.close("all")
            text = buffer.getvalue()
            if text:
                current_outputs.insert(0, _text_output(text))
            cell.outputs = current_outputs
        except Exception as exc:
            cell.outputs = [_text_output(buffer.getvalue()), nbformat.v4.new_output(
                "error", ename=type(exc).__name__, evalue=str(exc), traceback=traceback.format_exc().splitlines()
            )]
            nbformat.write(notebook, path)
            raise RuntimeError(f"Notebook failed at execution cell {execution_count}") from exc
    nbformat.write(notebook, path)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("notebooks/LaptopDSS_End_to_End_Audit.ipynb")
    execute(target)
    print(f"Executed and saved outputs: {target}")
