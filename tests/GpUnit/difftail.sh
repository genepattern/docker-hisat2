#!/bin/bash
tail -n +1 $1 > tail1
tail -n +1 $2 > tail2
diff tail1 tail2
