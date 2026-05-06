diff --git a/bot/move_ordering.py b/bot/move_ordering.py
--- a/bot/move_ordering.py
+++ b/bot/move_ordering.py
@@ -21,4 +21,6 @@ def move_score(board: chess.Board, move: chess.Move) -> int:
     if board.gives_check(move):
-        score += 75
+        score += 150
+    if move.to_square in {chess.D4, chess.E4, chess.D5, chess.E5}:
+        score += 20
     if not config.CAPTURE_FIRST:
         score = -score
