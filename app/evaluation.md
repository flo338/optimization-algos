## Args
```
options:
  -h, --help            show this help message and exit
  -b BOX_SIZE, --box_size BOX_SIZE
                        The Edge length of the boxes
  -minw MIN_WIDTH, --min_width MIN_WIDTH
                        Minimum width of rectangles
  -maxw MAX_WIDTH, --max_width MAX_WIDTH
                        Maximum width of rectangles
  -minh MIN_HEIGHT, --min_height MIN_HEIGHT
                        Minimum height of rectangles
  -maxh MAX_HEIGHT, --max_height MAX_HEIGHT
                        Maximum height of rectangles
  -rectnb RECTANGLE_NUMBER, --rectangle_number RECTANGLE_NUMBER
                        Number of rectangles
  -a ALGORITHM, --algorithm ALGORITHM
                        Name of the algorithm
  -t TEMPERATURE, --temperature TEMPERATURE
                        Temperature
  -cs COOLING_SCHEDULE, --cooling_schedule COOLING_SCHEDULE
                        Cooling schedule
```


## Usage:
```python evaluation.py -rectnb 100 -a "Simulated Annealing"```\
```python evaluation.py -rectnb 1000 -a "Simulated Annealing"```

```python evaluation.py -rectnb 100 -a Backtracking```\
```python evaluation.py -rectnb 1000 -a Backtracking```
