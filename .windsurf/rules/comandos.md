---
trigger: always_on
---

When running commands in the fish shell, check the $status variable instead of $? to determine if a command has completed successfully. Example: if test $status -eq 0 instead of if [ $? -eq 0 ]