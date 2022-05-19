from evaluation import evaluation

def test(model, device, train_edge_index, val_edge_index, test_edge_index, test_sparse_edge_index, contants):
    # evaluate on test set
    model.eval()
    test_edge_index = test_edge_index.to(device)
    test_sparse_edge_index = test_sparse_edge_index.to(device)

    test_loss, test_recall, test_precision, test_ndcg = evaluation(
                model, test_edge_index, test_sparse_edge_index, [train_edge_index, val_edge_index], contants["K"], contants["LAMBDA"])

    print(f"[test_loss: {round(test_loss, 5)}, test_recall@{contants['K']}: {round(test_recall, 5)}, test_precision@{contants['K']}: {round(test_precision, 5)}, test_ndcg@{contants['K']}: {round(test_ndcg, 5)}")