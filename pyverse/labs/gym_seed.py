"""Starter exercises. `manage.py seed_gym` loads them; test_gym.py verifies every one."""

SEED = [
    dict(
        slug="py-word-freq",
        title="Word frequencies",
        library="python",
        difficulty=1,
        prompt="<p>Write <code>word_freq(text)</code>: a dict of lowercase word &rarr; count. Split on whitespace, ignore case.</p>",
        setup_code="",
        starter_code='def word_freq(text):\n    ...\n\n\nword_freq("the cat the hat")\n',
        check_code=(
            'assert word_freq("the cat the hat") == {"the": 2, "cat": 1, "hat": 1}, "basic counts"\n'
            'assert word_freq("A a  A") == {"a": 3}, "ignore case and extra spaces"\n'
            'assert word_freq("") == {}, "empty string"\n'
        ),
        solution_code=(
            "from collections import Counter\n\n\n"
            "def word_freq(text):\n    return dict(Counter(text.lower().split()))\n"
        ),
        hints="Normalise first: lower() then split().\ncollections.Counter does the counting.",
    ),
    dict(
        slug="py-flatten",
        title="Flatten nested lists",
        library="python",
        difficulty=2,
        prompt="<p>Write <code>flatten(xs)</code> that flattens arbitrarily nested <em>lists</em> into one list, keeping order. Other types (strings, tuples) are left whole.</p>",
        setup_code="",
        starter_code="def flatten(xs):\n    ...\n",
        check_code=(
            "assert flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5], 'nested'\n"
            "assert flatten([]) == [], 'empty'\n"
            "assert flatten([[[]], 1]) == [1], 'empty inner lists'\n"
            "assert flatten(['ab', [('c',)]]) == ['ab', ('c',)], 'only lists are flattened'\n"
        ),
        solution_code=(
            "def flatten(xs):\n    out = []\n    for x in xs:\n"
            "        out.extend(flatten(x) if isinstance(x, list) else [x])\n    return out\n"
        ),
        hints="Recursion: a list element is a smaller instance of the same problem.",
    ),
    dict(
        slug="np-zscore",
        title="Standardise columns",
        library="numpy",
        difficulty=2,
        prompt="<p><code>X</code> is a 100&times;4 array. Build <code>Z</code>: each column shifted to mean 0 and scaled to std 1. No loops.</p>",
        setup_code="import numpy as np\nrng = np.random.default_rng(0)\nX = rng.normal(5, 3, (100, 4))\n",
        starter_code="Z = ...\n",
        check_code=(
            "assert Z.shape == X.shape, 'same shape as X'\n"
            "assert np.allclose(Z.mean(axis=0), 0), 'column means should be 0'\n"
            "assert np.allclose(Z.std(axis=0), 1), 'column stds should be 1'\n"
        ),
        solution_code="Z = (X - X.mean(axis=0)) / X.std(axis=0)\n",
        hints="axis=0 reduces down the rows, leaving one value per column.\nBroadcasting lines a (4,) vector up against (100, 4).",
    ),
    dict(
        slug="np-mask",
        title="Zero out negatives",
        library="numpy",
        difficulty=1,
        prompt="<p>Make <code>clipped</code>: a copy of <code>a</code> with every negative replaced by 0. Leave <code>a</code> unchanged.</p>",
        setup_code="import numpy as np\na = np.array([3, -1, 4, -1, 5, -9])\n",
        starter_code="clipped = ...\n",
        check_code=(
            "assert np.array_equal(clipped, [3, 0, 4, 0, 5, 0]), 'values wrong'\n"
            "assert a[1] == -1, 'do not modify a in place'\n"
        ),
        solution_code="clipped = np.where(a < 0, 0, a)\n",
        hints="A boolean mask a < 0 selects the negatives.\nnp.where(cond, x, y) builds a new array.",
    ),
    dict(
        slug="pd-top-spenders",
        title="Top two spenders",
        library="pandas",
        difficulty=1,
        prompt="<p>Using <code>df</code>, build <code>top</code>: a Series of the 2 customers with the highest <em>total</em> amount, largest first.</p>",
        setup_code='import pandas as pd\ndf = pd.DataFrame({"customer": list("ABCABCDA"), "amount": [10, 20, 5, 30, 15, 25, 40, 5]})\ndf\n',
        starter_code="top = ...\ntop\n",
        check_code=(
            'assert top.to_dict() == {"A": 45, "D": 40}, "expected totals A=45, D=40"\n'
            'assert list(top.index) == ["A", "D"], "largest first"\n'
        ),
        solution_code='top = df.groupby("customer")["amount"].sum().nlargest(2)\ntop\n',
        hints="groupby + sum gives totals per customer.\nSeries.nlargest(n) sorts for you.",
    ),
    dict(
        slug="pd-fill-group-mean",
        title="Fill gaps with the group mean",
        library="pandas",
        difficulty=2,
        prompt="<p>Fill each missing <code>score</code> with the mean score of that row&rsquo;s <code>team</code>. Modify <code>df</code> in place.</p>",
        setup_code='import numpy as np, pandas as pd\ndf = pd.DataFrame({"team": ["x", "x", "y", "y", "y"], "score": [1.0, np.nan, 4.0, np.nan, 8.0]})\n',
        starter_code="df\n",
        check_code='assert df["score"].tolist() == [1.0, 1.0, 4.0, 6.0, 8.0], "x gap -> 1.0, y gap -> 6.0"\n',
        solution_code='df["score"] = df.groupby("team")["score"].transform(lambda s: s.fillna(s.mean()))\ndf\n',
        hints="transform returns a result aligned to the original rows.",
    ),
    dict(
        slug="sns-histogram",
        title="Titled histogram",
        library="seaborn",
        difficulty=1,
        prompt="<p>Draw a histogram of <code>df['height']</code> with exactly 12 bins and the title <code>Heights</code>.</p>",
        setup_code=(
            "import numpy as np, pandas as pd, seaborn as sns, matplotlib.pyplot as plt\n"
            "rng = np.random.default_rng(1)\ndf = pd.DataFrame({'height': rng.normal(170, 8, 300)})\n"
        ),
        starter_code="# your plot here\n",
        check_code=(
            "ax = plt.gca()\n"
            "assert ax.get_title() == 'Heights', 'title should be Heights'\n"
            "assert len(ax.patches) == 12, 'expected 12 bars, got %d' % len(ax.patches)\n"
        ),
        solution_code="ax = sns.histplot(df, x='height', bins=12)\nax.set_title('Heights')\n",
        hints="sns.histplot returns the Axes it drew on.\nbins=12, then ax.set_title(...).",
    ),
]
