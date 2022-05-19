from util import sample_mini_batch
from evaluation import evaluation
from loss import bpr_loss

import wandb


def train(model, optimizer, scheduler, train_sparse_edge_index, train_edge_index, val_sparse_edge_index, val_edge_index, contants, device):
    for iter in range(contants['ITERATIONS']):
        # forward propagation
        users_emb_final, users_emb_0, items_emb_final, items_emb_0 = model.forward(
            train_sparse_edge_index)
        item_number = items_emb_0.shape[0]

        # mini batching
        user_indices, pos_item_indices, neg_item_indices = sample_mini_batch(
            contants['BATCH_SIZE'], train_edge_index, item_number)
        user_indices, pos_item_indices, neg_item_indices = user_indices.to(
            device), pos_item_indices.to(device), neg_item_indices.to(device)

        users_emb_final, users_emb_0 = users_emb_final[user_indices], users_emb_0[user_indices]
        pos_items_emb_final, pos_items_emb_0 = items_emb_final[
            pos_item_indices], items_emb_0[pos_item_indices]
        neg_items_emb_final, neg_items_emb_0 = items_emb_final[
            neg_item_indices], items_emb_0[neg_item_indices]

        # loss computation
        train_loss = bpr_loss(users_emb_final, users_emb_0, pos_items_emb_final,
                              pos_items_emb_0, neg_items_emb_final, neg_items_emb_0, contants['LAMBDA'])

        optimizer.zero_grad()
        train_loss.backward()
        optimizer.step()

        if iter % contants['ITERS_PER_EVAL'] == 0:
            model.eval()
            val_loss, recall, precision, ndcg = evaluation(
                model, val_edge_index, val_sparse_edge_index, [train_edge_index], contants['K'], contants['LAMBDA'])
            print(f"[Iteration {iter}/{contants['ITERATIONS']}] train_loss: {round(train_loss.item(), 5)}, val_loss: {round(val_loss, 5)}, val_recall@{contants['K']}: {round(recall, 5)}, val_precision@{contants['K']}: {round(precision, 5)}, val_ndcg@{contants['K']}: {round(ndcg, 5)}")

            wandb.log({
                "training_loss": train_loss.item(),
                "testing_loss": val_loss,
                "recall": round(recall, 5),
                "precision": round(precision, 5),
                "ndcg": round(ndcg, 5)
            })

            model.train()

        if iter % contants['ITERS_PER_LR_DECAY'] == 0 and iter != 0:
            scheduler.step()
