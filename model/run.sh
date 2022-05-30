# python3 main.py --name "delete duplicate (20) -> K=5" --iteration 10000 --batch-size 1024 --lr-decay 10000 --K 5 --embedding 64 --lambdas 0.000001
# python3 main.py --name "delete duplicate (20) -> K=7" --iteration 10000 --batch-size 1024 --lr-decay 10000 --K 7 --embedding 64 --lambdas 0.000001
# python3 main.py --name "delete duplicate (20) -> lr-decay 2000" --iteration 10000 --batch-size 1024 --lr-decay 2000 --K 3 --embedding 64 --lambdas 0.000001
# python3 main.py --name "delete duplicate (20) -> lambda 10" --iteration 10000 --batch-size 1024 --lr-decay 2000 --K 3 --embedding 64 --lambdas 10
#  python3 main.py --name "MovieLens small" --iteration 10000 --batch-size 1024 --lr-decay 200 --K 3 --embedding 8 --lambdas 0.000001
#  python3 main.py --name "MovieLens small -> K=20" --iteration 10000 --batch-size 1024 --lr-decay 200 --K 20 --embedding 8 --lambdas 0.000001
 python3 main.py --name "Add edge_attr (tag * commentNum (1, 1, 1))" --iteration 10000 --batch-size 1024 --lr-decay 200 --K 3 --embedding 8 --lambdas 0.000001