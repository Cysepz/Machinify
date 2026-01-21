# Machinify: SIC/XE Two-Pass Assembler

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![pytest](https://img.shields.io/badge/test-pytest-yellowgreen.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A robust, object-oriented implementation of a **SIC/XE (Simplified Instructional Computer Extra Equipment)** Assembler. This tool translates SIC/XE assembly source code into machine-executable object programs, supporting a wide range of addressing modes and instruction formats.



## Features

- **Two-Pass Architecture**:
    - **Pass 1**: Performs syntax analysis, builds the Symbol Table (SYMTAB), and calculates the Location Counter (LOCCTR).
    - **Pass 2**: Generates machine code, handles displacement calculations, and produces the final Object Program (H, T, E records).
- **Comprehensive Addressing Modes**:
    - Immediate (`#`), Indirect (`@`), and Indexed (`,X`).
    - Program Counter (PC) Relative and Base Relative addressing.
    - Extended format (Format 4) support (`+`).
- **Instruction Support**: Fully supports Format 1, 2, 3, and 4 instructions along with essential directives: `START`, `END`, `BYTE`, `WORD`, `RESB`, `RESW`, and `BASE`.
- **Advanced Error Detection**: Integrated logging system (`LogFile`) capable of detecting syntax errors, duplicate labels, invalid operands, and out-of-range addressing displacements.
- **Automated Regression Testing**: Integrated with the `pytest` framework and Golden File comparison logic to ensure assembly accuracy across different versions.

---

## Project Structure

The project is designed with modularity in mind, separating concerns into distinct classes for better maintainability:

| Component | Description |
| :--- | :--- |
| `OpTable` | Manages the opcode set, instruction formats, and mnemonic lookups. |
| `SymbolTable` | Handles label resolution and hardware register mapping. |
| `IntermediateFile` | Manages the persistent data stream between Pass 1 and Pass 2. |
| `ObjectFile` | Formats and outputs the machine code according to SIC/XE standards. |
| `test_assembler.py` | Automated CI-ready test suite using `pytest` for regression testing. |

---

## Getting Started

### Prerequisites
- Python 3.10 or higher.
- `pytest` (optional, for running the test suite).

### Installation
1. Clone the repository
   ```bash
   git clone [https://github.com/your-username/sicxe-assembler.git](https://github.com/your-username/sicxe-assembler.git)
   cd sicxe-assembler
2. Ensure opCode.txt is present in the root directory (formatted as MNEMONIC OPCODE).
### Usage
Run the assembler by providing the input file and output directory
    ```bash
    python assembler.py ./input/source.txt ./output
    ```
## Output Specifications
Upon successful assembly, the system generates three primary files:
### 1. Intermediate File (*_intermediate.txt)
A detailed trace file containing the following fields:
* **LINE**: Line number in the source program (input file).
* **LOC**: Location Counter.
    * Directive instructions will be marked as `-----`.
    * Mnemonic instructions are recorded in decimal format.
* **SOURCE PROGRAM**:
    * **Label**: The true label of the line or `-----`(Never empty).
    * **Operation**: The instruction mnemonic or directive (Never empty).
    * **Operand**: The target value or `-----` for null values (Never empty).
* **FORMAT**: The format of the operation (1~4); may be empty for directives.
* **OPCODE**: The opcode of the operation; may be empty for directives.
* **BIT FLAG**: A 6-bit string representing **nixbpe** flags; may be empty.

### 2. Object File (*_object.txt)
* **H (Header)**: Program name, starting address, and length.
* **T (Text)**: Actual machine instructions in hex.
* **E (End)**: First executable instruction address.

### 3. Log File (*_log.txt)
Detailed logs documenting the assembly process, warnings, and syntax errors detected during both passes.
---
## Testing & Quality Assurance

This project utilizes **Regression Testing** against "Golden Files" (verified standard outputs). This ensures that new features or refactors do not break existing functionality.

To execute the test suite:
```bash
pip install pytest
pytest -v
```
The test suite automatically compiles source files from ./input and compares the results against the standards in ./golden, reporting any line-by-line mismatches.

---

## Development Roadmap (TODO)
- [ ] Add support for **Literals** (LITTAB/LTORG).
- [ ] Optimize **Modification Records** (M Record) to support Format 4 relocation.

---

## 📄 License

This project is licensed under the **MIT License**. It is open for academic exchange and free use. See the LICENSE file for more details.