import numpy as np
import torch
import torch.nn as nn
import copy

from collections import OrderedDict
from baseline_constants import BYTES_WRITTEN_KEY, BYTES_READ_KEY


class Server:

    def __init__(self, client_model):
        self.client_model = copy.deepcopy(client_model)
        self.model = copy.deepcopy(client_model.state_dict())
        self.selected_clients = []
        self.updates = []

    def select_clients(self, my_round, possible_clients, num_clients=20):
        """Selects num_clients clients randomly from possible_clients.
        
        Note that within function, num_clients is set to
            min(num_clients, len(possible_clients)).

        Args:
            possible_clients: Clients from which the server can select.
            num_clients: Number of clients to select; default 20
        Return:
            list of (num_train_samples, num_test_samples)
        """
        num_clients = min(num_clients, len(possible_clients))
        np.random.seed(my_round)
        self.selected_clients = np.random.choice(possible_clients, num_clients, replace=False)

        return [(c.num_train_samples, c.num_test_samples) for c in self.selected_clients]

    def train_model(self, num_epochs=1, batch_size=10, minibatch=None, clients=None):
        """Trains self.model on given clients.
        
        Trains model on self.selected_clients if clients=None;
        each client's data is trained with the given number of epochs
        and batches.

        Args:
            clients: list of Client objects.
            num_epochs: Number of epochs to train.
            batch_size: Size of training batches.
            minibatch: fraction of client's data to apply minibatch sgd,
                None to use FedAvg
        Return:
            bytes_written: number of bytes written by each client to server 
                dictionary with client ids as keys and integer values.
            bytes_read: number of bytes read by each client from server
                dictionary with client ids as keys and integer values.
        """
        if clients is None:
            clients = self.selected_clients
        sys_metrics = {
            c.id: {BYTES_WRITTEN_KEY: 0,
                   BYTES_READ_KEY: 0,
                   } for c in clients}

        for c in clients:
            c.model.load_state_dict(self.model)
            num_samples, update = c.train(num_epochs, batch_size, minibatch)
            if isinstance(c.model, torch.nn.DataParallel):
                sys_metrics[c.id][BYTES_READ_KEY] += c.model.module.size
                sys_metrics[c.id][BYTES_WRITTEN_KEY] += c.model.module.size
            else:
                sys_metrics[c.id][BYTES_READ_KEY] += c.model.size
                sys_metrics[c.id][BYTES_WRITTEN_KEY] += c.model.size

            self.updates.append((num_samples, copy.deepcopy(update)))

        return sys_metrics

    def update_model(self):
        """FedAvg on the clients' updates for the current round.

        Weighted average of self.updates, where the weight is given by the number
        of samples seen by the corresponding client at training time.

        Saves the new central model in self.client_model and its state dictionary in self.model
        """
        total_weight = 0.
        base = OrderedDict()
        for (client_samples, client_model) in self.updates:
            total_weight += client_samples
            for key, value in client_model.items():
                if key in base:
                    base[key] += (client_samples * value.type(torch.FloatTensor))
                else:
                    base[key] = (client_samples * value.type(torch.FloatTensor))

        averaged_soln = copy.deepcopy(self.model)
        for key, value in base.items():
            if total_weight != 0:
                averaged_soln[key] = value.to('cpu') / total_weight

        # diff = sum((x - y).abs().sum() for x, y in zip(self.model.values(), averaged_soln.values()))
        # print("before and after difference: ", diff)

        self.client_model.load_state_dict(averaged_soln)
        self.model = copy.deepcopy(self.client_model.state_dict())
        self.updates = []

    def test_model(self, clients_to_test, batch_size, set_to_use='test'):
        """Tests self.model on given clients.

        Tests model on self.selected_clients if clients_to_test=None.
        For each client, the current server model is loaded before testing it.

        Args:
            clients_to_test: list of Client objects.
            set_to_use: dataset to test on. Should be in ['train', 'test'].
        """
        metrics = {}

        if clients_to_test is None:
            clients_to_test = self.selected_clients

        for client in clients_to_test:
            client.model.load_state_dict(self.model)
            c_metrics = client.test(batch_size, set_to_use)
            metrics[client.id] = c_metrics

        return metrics

    def get_clients_info(self, clients):
        """Returns the ids, hierarchies and num_samples for the given clients.

        Returns info about self.selected_clients if clients=None;

        Args:
            clients: list of Client objects.
        """
        if clients is None:
            clients = self.selected_clients

        ids = [c.id for c in clients]
        groups = {c.id: c.group for c in clients}
        num_samples = {c.id: c.num_samples for c in clients}
        return ids, groups, num_samples

    def save_model(self, path):
        """Saves the server model on checkpoints/dataset/model.ckpt."""
        # Save server model
        # self.client_model.load_state_dict(self.model)
        torch.save(self.model, path)
        return path

    def num_parameters(self, params):
        return sum(p.numel() for p in params if p.requires_grad)
