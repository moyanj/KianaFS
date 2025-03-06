def priority_to_probability(priorities: list) -> list:
    """
    将优先级列表转换为概率列表。

    :param priorities: 优先级列表，数值越小表示优先级越高。
    :return: 概率列表，总和为 1。
    """
    # 将优先级转换为权重（优先级越高，权重越大）
    weights = [1 / p for p in priorities]

    # 计算总权重
    total_weight = sum(weights)

    # 计算每个任务的概率
    probabilities = [w / total_weight for w in weights]

    return probabilities
