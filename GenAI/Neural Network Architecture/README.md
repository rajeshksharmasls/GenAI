# Neural Network Architecture and Backpropagation

## Overview

This project presents a feedforward neural network for a **binary classification** task: predicting whether a customer will buy a product after browsing an e-commerce website.
The network satisfies the assignment requirement of using at least **2 hidden layers** and at least **5 neurons in each hidden layer**.

## Problem Statement

The goal is to predict customer purchase behavior:

- `1` = customer buys the product
- `0` = customer does not buy the product

### Input Features

The model uses 6 input features:

1. Customer age
2. Time spent on the website
3. Number of items in cart
4. Previous purchases
5. Device used
6. Promo code used

An example input vector is:

```text
x = [28, 15, 3, 4, 1, 1]
```

## Neural Network Architecture

The architecture is a fully connected feedforward neural network.

| Layer | Neurons | Activation |
|-------|---------|------------|
| Input Layer | 6 | None |
| Hidden Layer 1 | 5 | ReLU |
| Hidden Layer 2 | 5 | ReLU |
| Output Layer | 1 | Sigmoid |

### Why these activations?

- **ReLU** is used in hidden layers because it introduces non-linearity and outputs the input when it is positive, otherwise zero.
- **Sigmoid** is used in the output layer because this is a binary classification problem, and it produces a probability between 0 and 1.

## Forward Propagation

Let the input be:

```text
a(0) = x
```

For each layer `l`, the forward propagation equations are:

```text
z(l) = W(l) a(l-1) + b(l)
a(l) = f(z(l))
```

### Layer-wise equations

#### Hidden Layer 1

```text
z(1) = W(1)x + b(1)
a(1) = ReLU(z(1))
```

#### Hidden Layer 2

```text
z(2) = W(2)a(1) + b(2)
a(2) = ReLU(z(2))
```

#### Output Layer

```text
z(3) = W(3)a(2) + b(3)
a(3) = sigmoid(z(3)) = 1 / (1 + e^(-z(3)))
```

The final output `a(3)` represents the predicted probability that the customer will make a purchase.

## Example Prediction

Using the example input and sample initialized weights, the final output is:

```text
a(3) ≈ 0.982
```

This means the model predicts a **98.2% probability** that the customer will buy the product.

## Loss Function

Since the task is binary classification, the loss function is **binary cross-entropy**:

```text
L = -[ y log(a(3)) + (1-y) log(1-a(3)) ]
```

where:

- `y` = actual label
- `a(3)` = predicted probability

If `y = 1` and `a(3) = 0.982`, then the loss is very small because the prediction is close to the true value.

## Backpropagation

Backpropagation computes the gradient of the loss with respect to each weight and bias using the **chain rule**.
The general gradient descent update rule is:

```text
W_ij(l) = W_ij(l) - η * ∂L/∂W_ij(l)
b_i(l)  = b_i(l)  - η * ∂L/∂b_i(l)
```

where `η` is the learning rate.

## Chain Rule for Weight Update

For a weight connecting neuron `j` in layer `l-1` to neuron `i` in layer `l`:

```text
∂L/∂W_ij(l) = ∂L/∂z_i(l) * ∂z_i(l)/∂W_ij(l)
```

Since:

```text
z_i(l) = Σ W_ij(l) a_j(l-1) + b_i(l)
```

we get:

```text
∂z_i(l)/∂W_ij(l) = a_j(l-1)
```

Therefore:

```text
∂L/∂W_ij(l) = δ_i(l) * a_j(l-1)
```

where:

```text
δ_i(l) = ∂L/∂z_i(l)
```

So the final weight update formula is:

```text
W_ij(l) = W_ij(l) - η * δ_i(l) * a_j(l-1)
```

And the bias update formula is:

```text
b_i(l) = b_i(l) - η * δ_i(l)
```

This is the standard backpropagation result obtained through the chain rule.

## Error Terms for Each Layer

### 1. Output Layer Error

For the output layer:

```text
δ(3) = a(3) - y
```

This form is obtained when using sigmoid activation with binary cross-entropy loss.

### 2. Hidden Layer 2 Error

The error is propagated backward from the output layer:

```text
δ(2) = (W(3)^T δ(3)) * f'(z(2))
```

For ReLU:

```text
f'(z) = 1, if z > 0
f'(z) = 0, if z <= 0
```

So only neurons with positive pre-activation pass gradient backward.

### 3. Hidden Layer 1 Error

Similarly,

```text
δ(1) = (W(2)^T δ(2)) * f'(z(1))
```

## Layer-wise Weight Updates

### Output Layer

```text
∂L/∂W_i(3) = δ(3) * a_i(2)
W_i(3) = W_i(3) - η * δ(3) * a_i(2)
b(3)   = b(3)   - η * δ(3)
```

### Hidden Layer 2

```text
∂L/∂W_ij(2) = δ_i(2) * a_j(1)
W_ij(2) = W_ij(2) - η * δ_i(2) * a_j(1)
b_i(2)  = b_i(2) - η * δ_i(2)
```

### Hidden Layer 1

```text
∂L/∂W_ij(1) = δ_i(1) * x_j
W_ij(1) = W_ij(1) - η * δ_i(1) * x_j
b_i(1)  = b_i(1) - η * δ_i(1)
```

## Training Steps

The neural network is trained iteratively using the following steps:

1. Initialize weights and biases.
2. Perform forward propagation.
3. Compute the loss.
4. Perform backpropagation using the chain rule.
5. Update weights and biases using gradient descent.
6. Repeat for multiple epochs until the loss decreases.

## Key Points

- This is a **binary classification** neural network.
- It contains **2 hidden layers** with **5 neurons each**.
- Hidden layers use **ReLU** activation.
- Output layer uses **sigmoid** activation.
- Weight updates are computed using **chain rule + backpropagation**.

## Conclusion

This neural network architecture is suitable for predicting customer purchase behavior using browsing and customer-related features.
The backpropagation algorithm updates each weight efficiently by computing gradients layer by layer with the chain rule, making learning possible in multi-layer neural networks.
