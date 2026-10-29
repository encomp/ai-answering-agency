# Event Ordering and Consistency Models in Distributed Systems

Explore event ordering and consistency models in distributed systems to learn how different approaches like total, partial, and causal ordering balance consistency, performance, and user experience. Understand how these concepts influence consistency guarantees such as strong, causal, and eventual consistency in distributed databases, preparing you to design and analyze scalable, reliable systems.

We'll cover the following...

- [Event ordering models](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Event-ordering-models)
  - [Total ordering](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Total-ordering)
  - [Partial ordering](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Partial-ordering)
  - [Causal ordering](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Causal-ordering)
- [Consistency models in distributed databases](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Consistency-models-in-distributed-databases)
  - [Strong consistency](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Strong-consistency)
  - [Causal consistency](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Causal-consistency)
  - [Eventual consistency](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Eventual-consistency)
- [Conclusion](https://www.educative.io/courses/grokking-system-design-fundamentals/event-ordering-and-consistency-models#Conclusion)

In the previous lesson, we explored mechanisms such as Lamport clocks and vector clocks that help determine whether events in a distributed system are causally related or concurrent.

While these tools clarify relationships between events, they don’t provide a definitive protocol for ordering those events across the system. This leads to a bigger question: Given what we know about causal and concurrent relationships, how should a system decide the final order of events?

That’s where ordering models come into play.

Ordering models define the rules a distributed system follows to determine the sequence in which events are processed or applied across all nodes. Each model offers a distinct balance between consistency, performance, and user experience, enabling system designers to select the approach that best suits their requirements.

**Example:** If two users post comments concurrently on a social media platform, clocks can indicate whether the actions are causally or temporally related. However, it’s the ordering model that determines whether those comments should appear in the same order for everyone or can be displayed in any order.

To understand these models more clearly, let’s explore how each one defines the rules for sequencing events in a distributed system and how those choices shape system behavior.

## Event ordering models

In this section, we’ll look at the three main event ordering models in detail: total ordering, partial ordering, and causal ordering. While there are other models, such as FIFO, sequential, and real-time ordering, these three are fundamental to how distributed systems handle event consistency.

By walking through them one by one, we’ll see how they affect both the system and the end user.

### Total ordering

In total ordering, every event in the system is arranged into one single, global sequence. This means that, regardless of which server (or node) processes the events, they all agree on the exact same order. As a result, even if multiple events occur simultaneously, the system selects a consistent order, ensuring that all users view those events in the exact sequence, as illustrated below.

Total ordering ensures that all users see events in the same order...

