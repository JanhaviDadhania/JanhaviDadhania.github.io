# Executive Summary

The tournament converged on a single top-ranked hypothesis exploring how Sparse Autoencoder (SAE) feature-splitting hierarchies might encode causal structure within neural networks [H-hyp_bd0afd5bcfef5d20]. The core idea — that features learned at smaller dictionary sizes are causally more central than those appearing only at larger sizes — is a compelling operationalization of mechanistic interpretability that bridges representation learning and causal inference. While the tournament was narrow in scope (only one hypothesis reached final ranking), this direction is well-motivated by recent empirical work on SAE scaling and feature geometry. Acting on it could yield a principled, falsifiable framework for evaluating whether SAEs do more than describe activations — whether they actually illuminate *how* models compute.

---

# Main Research Directions

## 1. SAE Feature-Splitting as a Causal Concept Hierarchy

- **The direction.** Train SAEs at multiple dictionary sizes on the same model and test whether "root" features (small SAEs) have greater causal effect on downstream task performance than "leaf" features (large SAEs).
- **Why it's promising.** [H-hyp_bd0afd5bcfef5d20] proposes a directly measurable prediction: activation-patching effect sizes should decrease monotonically as features appear at larger and larger dictionary scales. This is grounded in the well-documented phenomenon of feature splitting (first described in Anthropic's monosemanticity work) and connects it to a causal rather than merely descriptive account of SAE features. The hypothesis is attractive because it generates a concrete hierarchy that could be validated or refuted with existing tooling.
- **Open questions.**
  - Does feature splitting actually produce a *tree* structure, or a more tangled DAG? If features do not split cleanly, the causal-centrality prediction may not hold.
  - Are activation-patching effect sizes a reliable proxy for "causal centrality," or do they conflate direct and indirect causal pathways?
  - Does the hierarchy generalize across model families (e.g., GPT-style vs. BERT-style architectures), or is it an artifact of a specific training regime?
  - Could the observed hierarchy reflect data-frequency statistics rather than genuine causal structure in the model?
- **First experiment.** Train SAEs at 3–5 dictionary sizes (e.g., 512, 2048, 8192, 32768 features) on a single residual-stream layer of a small open-weight LLM (e.g., Pythia-1.4B or GPT-2-XL). For each feature, compute activation-patching effect sizes on 2–3 diverse downstream tasks (e.g., factual recall, syntax, sentiment). Test whether mean effect size is significantly higher for features present only in the smallest SAE vs. those appearing only in the largest. A Spearman rank correlation between "first-appearance dictionary size" and "median patching effect size" provides a single summary statistic. This can be completed in 4–8 weeks with standard interpretability libraries (TransformerLens, SAELens).

---

# Convergence and Divergence

Given that the tournament produced only **one ranked hypothesis**, there is no convergence or divergence across competing directions to report directly. This is an important caveat (see below). The single hypothesis, [H-hyp_bd0afd5bcfef5d20], sits at the intersection of two independently active research threads:

- **SAE scaling / feature geometry** (e.g., Anthropic's superposition and monosemanticity work): concerned with *what* features SAEs learn.
- **Causal mediation analysis in neural networks** (e.g., activation patching, path patching): concerned with *which* computations matter for behavior.

These threads are currently treated as largely orthogonal in the literature; this hypothesis proposes they are structurally linked. Whether that link is real or coincidental is the central open question.

---

# Caveats and Limitations

1. **Extremely thin tournament coverage.** Only one hypothesis was evaluated; the system did not explore alternative interpretability approaches (probing classifiers, circuits analysis, concept bottleneck models, TCAV, etc.) that could serve as controls or baselines for assessing SAE utility.

2. **No reviews were submitted.** The lone hypothesis carries no peer-style evaluation from other agents, meaning its assumptions have not been stress-tested within the tournament itself. The open questions listed above are speculative rather than tournament-validated.

3. **The causal-centrality claim is theoretically underspecified.** "Causal centrality" in neural networks is contested; activation patching measures a specific interventional quantity that can be confounded by feature correlations, attention sink effects, and nonlinear interactions. A domain expert would likely push back on equating patching effect size with causal importance.

4. **Feature splitting may not be hierarchical.** The hypothesis assumes splitting is tree-structured, but empirical evidence (e.g., from Bricken et al. 2023 and follow-ups) suggests feature geometry is complex. The causal-tree framing may impose more structure than exists.

5. **Evaluation tasks are unspecified.** The hypothesis mentions "diverse downstream tasks" but does not define what counts as a sufficient diversity. Task choice could heavily influence whether the hierarchy appears clean or noisy.

6. **No exploration of failure modes of SAEs as an interpretability tool.** The research goal is to *test* SAEs — a rigorous test requires null hypotheses and adversarial evaluations (e.g., do SAE features explain model errors? do they transfer across fine-tuning?). The tournament did not surface these critical perspectives.

**Recommendation for the scientist:** Before investing heavily in [H-hyp_bd0afd5bcfef5d20], run a broader hypothesis-generation phase that includes competing interpretability paradigms and explicit null hypotheses about SAE limitations. The current hypothesis is promising but represents a narrow slice of the design space.