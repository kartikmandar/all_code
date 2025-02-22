"""
Test script for all_code.py command-line arguments.

This script creates temporary directories and files, then uses the built-in
subprocess module to run all_code.py with different options:

- Default behavior (creates 'full_code.txt')
- Overriding the output file name with -o/--output-file
- Including only specific files with -i/--include-files
- Overriding programming extensions with -x/--extensions
- Excluding directories with -e/--exclude-dirs

No external libraries are required.
"""

import os
import shutil
import subprocess
import tempfile

SCRIPT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "all_code.py")


def run_script(args, cwd):
    """
    Run all_code.py with the provided command-line arguments in directory cwd.
    """
    cmd = ["python", SCRIPT_PATH] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result


def test_default_arguments():
    # Create a temporary directory to serve as the source for aggregation.
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy all_code.py to tmp directory  and run it without any args
        TMP_SCRIPT_PATH = shutil.copy(SCRIPT_PATH, tmp_dir)
        cmd = ["python", TMP_SCRIPT_PATH]
        subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True)

        assert os.path.exists(os.path.join(tmp_dir, "full_code.txt")), "full_code.txt not created by default"


def test_directory_argument():
    with tempfile.TemporaryDirectory() as source_dir:
        # Create a dummy Python file in the source directory.
        dummy_file = os.path.join(source_dir, "dummy.py")
        with open(dummy_file, "w") as f:
            f.write("print('Aggregating from source directory')")
        # Use a separate temporary directory as the working directory for the script.
        with tempfile.TemporaryDirectory() as tmp_working:
            custom_output = "test_output.txt"
            # Run the script with -d pointing to the source directory.
            run_script(["-d", source_dir, "-o", custom_output], cwd=tmp_working)
            output_file = os.path.join(tmp_working, custom_output)
            assert os.path.exists(output_file), "Output file not created when using --directory"
            with open(output_file, "r") as f:
                content = f.read()
            assert "dummy.py" in content, "Aggregated content does not reflect the --directory argument"
            print("test_directory_argument passed.")


def test_default_output():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy Python file so that there is something to include.
        dummy_file = os.path.join(tmpdir, "dummy.py")
        with open(dummy_file, "w") as f:
            f.write("print('Hello World')")

        # Run the script with default output (should create full_code.txt)
        run_script(["-d", tmpdir], cwd=tmpdir)
        output_file = os.path.join(tmpdir, "full_code.txt")
        assert os.path.exists(output_file), "Default output file not created"
        print("test_default_output passed.")


def test_override_output_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_file = os.path.join(tmpdir, "dummy.py")
        with open(dummy_file, "w") as f:
            f.write("print('Hello World')")

        custom_output = "custom_output.txt"
        run_script(["-d", tmpdir, "-o", custom_output], cwd=tmpdir)
        output_file = os.path.join(tmpdir, custom_output)
        assert os.path.exists(output_file), "Overridden output file not created"
        print("test_override_output_file passed.")


def test_include_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two Python files.
        file1 = os.path.join(tmpdir, "dummy.py")
        with open(file1, "w") as f:
            f.write("print('Hello from dummy')")

        file2 = os.path.join(tmpdir, "extra.py")
        with open(file2, "w") as f:
            f.write("print('Hello from extra')")

        # Specify only dummy.py to be included.
        run_script(["-d", tmpdir, "-i", "dummy.py"], cwd=tmpdir)
        output_file = os.path.join(tmpdir, "full_code.txt")
        with open(output_file, "r") as f:
            content = f.read()
        assert "dummy.py" in content, "dummy.py should be included"
        assert "print('Hello from extra')" not in content, "extra.py should not be included"
        print("test_include_files passed.")


def test_extensions():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create one .py file and one .txt file.
        py_file = os.path.join(tmpdir, "dummy.py")
        with open(py_file, "w") as f:
            f.write("print('Python file')")
        txt_file = os.path.join(tmpdir, "dummy.txt")
        with open(txt_file, "w") as f:
            f.write("This is a text file.")

        # Override extensions to only include .py files.
        run_script(["-d", tmpdir, "-x", ".py"], cwd=tmpdir)
        output_file = os.path.join(tmpdir, "full_code.txt")
        with open(output_file, "r") as f:
            content = f.read()
        assert "dummy.py" in content, "dummy.py should be included with .py extension"
        assert "This is a text file." not in content, "dummy.txt should be excluded when only .py is allowed"
        print("test_extensions passed.")


def test_exclude_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a subdirectory that will be excluded.
        exclude_dir = os.path.join(tmpdir, "exclude_me")
        os.mkdir(exclude_dir)
        file_in_excluded = os.path.join(exclude_dir, "dummy.py")
        with open(file_in_excluded, "w") as f:
            f.write("print('This file is in an excluded directory')")

        # Run the script with exclude_dirs set to 'exclude_me'
        run_script(["-d", tmpdir, "-e", "exclude_me"], cwd=tmpdir)
        output_file = os.path.join(tmpdir, "full_code.txt")
        with open(output_file, "r") as f:
            content = f.read()
        # The directory tree should mark exclude_me as excluded.
        assert "exclude_me/ [EXCLUDED]" in content, "exclude_me directory should be marked as excluded"
        # The file inside should not be aggregated.
        assert "dummy.py" not in content, "File inside excluded directory should not be included"
        print("test_exclude_dirs passed.")


if __name__ == "__main__":
    test_default_arguments()
    test_directory_argument()
    test_default_output()
    test_override_output_file()
    test_include_files()
    test_extensions()
    test_exclude_dirs()
    print("All tests passed!")
