import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.normalize import NO_CHANGE, canonical, files_touched, largest_cluster_share

P1 = """diff --git a/pkg/mod.py b/pkg/mod.py
index 1111111..2222222 100644
--- a/pkg/mod.py
+++ b/pkg/mod.py
@@ -10,7 +10,7 @@ def f(x):
     a = 1
-    return a + 1
+    return a + 2
     b = 2
"""

# same change: different index hashes, different hunk offsets/context, CRLF, trailing spaces
P2 = (
    "diff --git a/pkg/mod.py b/pkg/mod.py\r\n"
    "index aaaaaaa..bbbbbbb 100755\r\n"
    "--- a/pkg/mod.py\r\n"
    "+++ b/pkg/mod.py\t2026-01-01 00:00:00\r\n"
    "@@ -40,9 +40,9 @@ def f(x):\r\n"
    "     z = 0\r\n"
    "-    return a + 1   \r\n"
    "+    return a + 2\t\r\n"
    "     b = 2\r\n"
)

P3 = """diff --git a/pkg/mod.py b/pkg/mod.py
index 1111111..2222222 100644
--- a/pkg/mod.py
+++ b/pkg/mod.py
@@ -10,7 +10,7 @@ def f(x):
-    return a + 1
+    return a + 3
"""

TWO_FILES_A = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,2 +1,3 @@
 x = 1
+y = 2
diff --git a/b.py b/b.py
--- a/b.py
+++ b/b.py
@@ -5,2 +5,2 @@
-z = 3
+z = 4
"""

TWO_FILES_B = """diff --git a/b.py b/b.py
index 1..2 100644
--- a/b.py
+++ b/b.py
@@ -50,2 +50,2 @@
-z = 3
+z = 4
diff --git a/a.py b/a.py
index 3..4 100644
--- a/a.py
+++ b/a.py
@@ -9,2 +9,3 @@
 x = 1
+y = 2
"""

TABS = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1,1 +1,1 @@
-	return 1
+    return 1
"""


def test_index_hash_and_offsets_ignored():
    assert canonical(P1) == canonical(P2)


def test_changed_line_matters():
    assert canonical(P1) != canonical(P3)


def test_trailing_whitespace_ignored():
    a = "diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b\n"
    b = "diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a   \n+b\t\n"
    assert canonical(a) == canonical(b)


def test_file_order_ignored():
    assert canonical(TWO_FILES_A) == canonical(TWO_FILES_B)


def test_internal_whitespace_preserved():
    a = "diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-return 1\n+    return 1\n"
    assert canonical(a) != canonical(TABS)


def test_no_change_token():
    assert canonical("") == NO_CHANGE
    assert canonical("diff --git a/x b/x\nold mode 100644\nnew mode 100755\n") == NO_CHANGE
    assert canonical("just prose, not a diff") == NO_CHANGE


def test_new_file_and_dev_null():
    p = """diff --git a/new.py b/new.py
new file mode 100644
--- /dev/null
+++ b/new.py
@@ -0,0 +1,2 @@
+a = 1
+b = 2
"""
    assert files_touched(p) == ("new.py",)
    assert canonical(p) == "new.py\n+a = 1\n+b = 2"


def test_files_touched_sorted_and_unique():
    assert files_touched(TWO_FILES_A) == ("a.py", "b.py")
    # duplicate sections for one path collapse in the set
    dup = TWO_FILES_A + TWO_FILES_A
    assert files_touched(dup) == ("a.py", "b.py")


def test_quoted_paths_fallback():
    p = 'diff --git "a/sp ace.py" "b/sp ace.py"\n--- "a/sp ace.py"\n+++ "b/sp ace.py"\n@@ -1 +1 @@\n-x\n+y\n'
    assert files_touched(p) == ("sp ace.py",)


def test_largest_cluster_share():
    assert largest_cluster_share(["a", "b", "c"]) == 1 / 3
    assert largest_cluster_share(["a", "a", "b"]) == 2 / 3
    assert largest_cluster_share(["a", "a", "a"]) == 1.0
    assert largest_cluster_share([NO_CHANGE, NO_CHANGE, "x"]) == 2 / 3
