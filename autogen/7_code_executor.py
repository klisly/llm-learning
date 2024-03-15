from pathlib import Path
from autogen.coding import CodeBlock
from autogen.coding import DockerCommandLineCodeExecutor

work_dir = Path("coding")
work_dir.mkdir(exist_ok=True)

with DockerCommandLineCodeExecutor(work_dir=work_dir, 
    image="10.8.0.1:2080/library/yuzhi-python:py310",  # Execute code using the given docker image name.
    timeout=10,  # Timeout for each code execution in seconds.
    ) as executor:
    print(
        executor.execute_code_blocks(
            code_blocks=[
                CodeBlock(language="python", code="print('Hello, World!')"),
            ]
        )
    )