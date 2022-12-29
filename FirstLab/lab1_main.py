from threading import Thread
from time import perf_counter

import numpy as np
from matplotlib import pyplot as plt

from channel import Channel
from base_logger import StatsEnum
from GBN import Sender as SenderGBN, Receiver as ReceiverGBN
from SRP import Sender as SenderSRP, Receiver as ReceiverSRP


def plot(x, y, ax=None, xlabel=None, ylabel=None, title=None, **kwargs):
    if ax is None:
        _, ax = plt.subplots(1, 1)
    ax.plot(x, y, **kwargs)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)


def timeout_test():
    def experiment(window_size, timeout, loss_chance):
        sender = Sender(window_size=window_size, timeout=timeout)
        receiver = Receiver()
        channel_main = Channel(loss_chance=loss_chance)
        channel_back = Channel(loss_chance=0)
        sender_thread = Thread(target=sender.run, args=(channel_back, channel_main, data, False))
        receiver_thread = Thread(target=receiver.run, args=(channel_main, channel_back, False))

        time_start = perf_counter()
        sender_thread.start()
        receiver_thread.start()
        sender_thread.join()
        receiver_thread.join()
        time_elapsed = perf_counter() - time_start
        assert (receiver.data == data)
        msgs = sender.stats[StatsEnum.msg_derived] + sender.stats[StatsEnum.msg_lost]
        return msgs, time_elapsed

    data = list(range(50))
    for loss_chance in 0, 0.9:
        timeout = 0.1
        window_sizes = list(range(1, 11))
        msgs_sent = {}
        time_spent = {}
        for Sender, Receiver in (SenderGBN, ReceiverGBN), (SenderSRP, ReceiverSRP):
            protocol = 'GBN' if Sender == SenderGBN else 'SRP'
            msgs_sent[protocol] = []
            time_spent[protocol] = []
            for window_size in window_sizes:
                msgs, time_elapsed = experiment(window_size, timeout, loss_chance)
                msgs_sent[protocol].append(msgs)
                time_spent[protocol].append(time_elapsed)
        title = 'loss_chance = {}, timeout = {}'.format(loss_chance, timeout)
        _, ax = plt.subplots(1, 1)
        plot(window_sizes, msgs_sent['GBN'], ax, 'window_size', 'messages', title, label='GBN')
        plot(window_sizes, msgs_sent['SRP'], ax, label='SRP')
        ax.legend()
        _, ax = plt.subplots(1, 1)
        plot(window_sizes, time_spent['GBN'], ax, 'window_size', 'time spent', title, label='GBN')
        plot(window_sizes, time_spent['SRP'], ax, label='SRP')
        ax.legend()
        print(title)

        window_size = 5
        msgs_sent = {}
        time_spent = {}
        timeouts = np.linspace(0.1, 1, num=11)
        for Sender, Receiver in (SenderGBN, ReceiverGBN), (SenderSRP, ReceiverSRP):
            protocol = 'GBN' if Sender == SenderGBN else 'SRP'
            msgs_sent[protocol] = []
            time_spent[protocol] = []
            for timeout in timeouts:
                msgs, time_elapsed = experiment(window_size, timeout, loss_chance)
                msgs_sent[protocol].append(msgs)
                time_spent[protocol].append(time_elapsed)
        title = 'loss_chance = {}, window_size = {}'.format(loss_chance, window_size)
        _, ax = plt.subplots(1, 1)
        plot(timeouts, msgs_sent['GBN'], ax, 'timeout', 'messages', title, label='GBN')
        plot(timeouts, msgs_sent['SRP'], ax, label='SRP')
        ax.legend()
        _, ax = plt.subplots(1, 1)
        plot(timeouts, time_spent['GBN'], ax, 'timeout', 'time spent', title, label='GBN')
        plot(timeouts, time_spent['SRP'], ax, label='SRP')
        ax.legend()
        print(title)


timeout_test()
plt.show()
