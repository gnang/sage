r"""
Shuffle product of words
"""
#*****************************************************************************
#       Copyright (C) 2007 Mike Hansen <mhansen@gmail.com>,
#       Copyright (C) 2008 Franco Saliola <saliola@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
from sage.combinat.words.word import Word_class
from sage.combinat.combinat import CombinatorialClass
from sage.rings.all import binomial
from sage.combinat.integer_vector import IntegerVectors
from sage.combinat.subset import Subsets
from sage.combinat.composition import Compositions_n, Compositions

class ShuffleProduct_w1w2(CombinatorialClass):
    def __init__(self, w1, w2):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            sage: W = Words([1,2,3,4])
            sage: s = ShuffleProduct_w1w2(W([1,2]),W([3,4]))
            sage: s == loads(dumps(s))
            True
        """
        self._w1 = w1
        self._w2 = w2

    def __repr__(self):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            sage: W = Words("abcd")
            sage: repr(ShuffleProduct_w1w2(W("ab"),W("cd")))
            'Shuffle product of word: ab and word: cd'
        """
        return "Shuffle product of %s and %s"% (repr(self._w1), repr(self._w2))

    def __contains__(self, x):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            sage: W = Words("abcd")
            sage: w = W("ab")
            sage: u = W("cd")
            sage: S = ShuffleProduct_w1w2(w,u)
            sage: w*u in S
            True
            sage: all(w.is_subword_of(x) for x in S)
            True
            sage: w in S
            False

        We check that :trac:`14121` is solved::

            sage: w = W('ab')
            sage: x = W('ac')
            sage: x*w in w.shuffle(x)
            True
        """
        from sage.combinat.words.word import Word
        if not isinstance(x, Word_class):
            return False
        if x.length() !=self._w1.length() + self._w2.length():
            return False
        w1 = list(self._w1)
        w2 = list(self._w2)
        wx = list(x)
        for _ in range(len(wx)):
            try:
                letter = wx.pop(0)
            except IndexError:
                return False
            if len(w1) > 0 and len(w2) > 0 and letter == w1[0] == w2[0]:
                return Word(wx) in self._w1[1:].shuffle(self._w2) or Word(wx) in self._w1.shuffle(self._w2[1:])
            if len(w1) > 0 and letter == w1[0]:
                w1.pop(0)
            elif len(w2) > 0 and letter == w2[0]:
                w2.pop(0)
            else:
                return False
        return len(wx) == 0

    def cardinality(self):
        """
        Returns the number of words in the shuffle product
        of w1 and w2.

        It is given by binomial(len(w1)+len(w2), len(w1)).

        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            sage: w, u = map(Words("abcd"), ["ab", "cd"])
            sage: S = ShuffleProduct_w1w2(w,u)
            sage: S.cardinality()
            6
         """
        return binomial(self._w1.length()+self._w2.length(), self._w1.length())

    def _proc(self, vect):
        """
        Return the shuffle of ``w1`` with ``w2`` with 01-vector
        ``vect``.

        The 01-vector of a shuffle is a list of 0s and 1s whose
        length is the sum of the lengths of ``w1`` and ``w2``,
        and whose `k`-th entry is `1` if the `k`-th letter of
        the shuffle is taken from ``w1`` and `0` if it is taken
        from ``w2``.

        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            sage: w, u = map(Words("abcd"), ["ab", "cd"])
            sage: S = ShuffleProduct_w1w2(w,u)
            sage: S._proc([0,1,0,1])
            word: cadb
            sage: S._proc([1,1,0,0])
            word: abcd

            sage: I = Composition([1, 1])
            sage: J = Composition([2])
            sage: S = ShuffleProduct_w1w2(I, J)
            sage: S._proc([1,0,1])
            [1, 2, 1]

        TESTS:

        Sage is no longer confused by a too-restrictive parent
        of `I` when shuffling two compositions `I` and `J`
        (cf. :trac:`15131`)::

            sage: I = Composition([1, 1])
            sage: J = Composition([2])
            sage: S = ShuffleProduct_w1w2(I, J)
            sage: S._proc([1,0,1])
            [1, 2, 1]
        """
        i1 = -1
        i2 = -1
        res = []
        for v in vect:
            if v == 1:
                i1 += 1
                res.append(self._w1[i1])
            else:
                i2 += 1
                res.append(self._w2[i2])
        try:
            return self._w1.parent()(res)
        except ValueError:
            # Special situation: the parent of w1 is too
            # restrictive to be cast on res.
            if isinstance(self._w1.parent(), Compositions_n):
                return Compositions(res)

    def __iter__(self):
        """
        Return an iterator for the words in the
        shuffle product of ``w1`` and ``w2``.

        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_w1w2
            sage: w, u = map(Words("abcd"), ["ab", "cd"])
            sage: S = ShuffleProduct_w1w2(w,u)
            sage: S.list() #indirect test
            [word: abcd, word: acbd, word: acdb, word: cabd, word: cadb, word: cdab]
        """
        n1 = len(self._w1)
        n2 = len(self._w2)
        for iv in IntegerVectors(n1, n1+n2, max_part=1):
            yield self._proc(iv)

class ShuffleProduct_shifted(ShuffleProduct_w1w2):
    def __init__(self, w1, w2):
        """
        Shifted shuffle product of ``w1`` with ``w2``.

        This is the shuffle product of ``w1`` with the word
        obtained by adding the length of ``w1`` to every letter
        of ``w2``.

        Note that this class is meant to be used for words; it
        misbehaves when ``w1`` is a permutation or composition.

        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_shifted
            sage: w, u = Word([1,2]), Word([3,4])
            sage: S = ShuffleProduct_shifted(w,u)
            sage: S == loads(dumps(S))
            True
        """
        shift = w1.length()
        shifted_w2 = w1.parent()([x + shift for x in w2])
        ShuffleProduct_w1w2.__init__(self, w1, shifted_w2)

    def __repr__(self):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_shifted
            sage: w, u = Word([0,1]), Word([2,3])
            sage: ShuffleProduct_shifted(w,u).__repr__()
            'Shuffle product of word: 01 and word: 45'
        """
        return "Shuffle product of %s and %s"% (repr(self._w1), repr(self._w2))

class ShuffleProduct_overlapping_r(CombinatorialClass):
    def __init__(self, w1, w2, r):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping_r
            sage: w, u = map(Words("abcdef"), ["ab", "cd"])
            sage: S = ShuffleProduct_overlapping_r(w,u,1)
            sage: S == loads(dumps(S))
            True
        """
        self._w1 = w1
        self._w2 = w2
        self.r  = r
        self.W  = self._w1.parent()
        # Special situation: the parent of w1 is too
        # restrictive to be cast on the shuffles.
        if isinstance(self.W, Compositions_n):
            self.W = Compositions()

    def __repr__(self):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping_r
            sage: w, u = map(Words("abcdef"), ["ab", "cd"])
            sage: ShuffleProduct_overlapping_r(w,u,1).__repr__()
            'Overlapping shuffle product of word: ab and word: cd with 1 overlaps'
        """
        return "Overlapping shuffle product of %s and %s with %s overlaps"%(repr(self._w1), repr(self._w2), self.r)

    def __iter__(self):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping_r
            sage: w, u = Word([1,2]), Word([3,4])
            sage: ShuffleProduct_overlapping_r(w,u,1).list()
            [word: 424, word: 154, word: 442, word: 136, word: 352, word: 316]
            sage: w, u = map(Words(range(1,7)), [[1,2], [3,4]])
            sage: W = Words(range(1,7))
            sage: w, u = W([1,2]), W([3,4])
            sage: ShuffleProduct_overlapping_r(w, u, 1).list() #indirect doctest
            [word: 424, word: 154, word: 442, word: 136, word: 352, word: 316]

            sage: I, J = Composition([2, 2]), Composition([1, 1])
            sage: S = ShuffleProduct_overlapping_r(I, J, 1)
            sage: S.list()
            [[3, 2, 1], [2, 3, 1], [3, 1, 2], [2, 1, 3], [1, 3, 2], [1, 2, 3]]

        TESTS:

        Sage is no longer confused by a too-restrictive parent
        of `I` when shuffling two compositions `I` and `J`
        (cf. :trac:`15131`)::

            sage: I, J = Compositions(4)([2, 2]), Composition([1, 1])
            sage: S = ShuffleProduct_overlapping_r(I, J, 1)
            sage: S.list()
            [[3, 2, 1], [2, 3, 1], [3, 1, 2], [2, 1, 3], [1, 3, 2], [1, 2, 3]]
        """
        W = self.W

        m = len(self._w1)
        n = len(self._w2)
        r = self.r

        wc1, wc2 = self._w1, self._w2

        blank = [0]*(m+n-r)
        for iv in IntegerVectors(m, m+n-r, max_part=1):
            w = blank[:]
            filled_places = []
            unfilled_places = []
            #Fill in w1 into the iv slots
            i = 0
            for j in range(len(iv)):
                if iv[j] == 1:
                    w[j] = wc1[i]
                    i += 1
                    filled_places.append(j)
                else:
                    unfilled_places.append(j)

            #Choose r of these filled places
            for subset in Subsets(filled_places, r):
                places_to_fill = unfilled_places + list(subset)
                places_to_fill.sort()

                #Fill in w2 into the places
                i = 0
                res = w[:]
                for j in places_to_fill:
                    res[j] += wc2[i]
                    i += 1

                yield W(res)

class ShuffleProduct_overlapping(CombinatorialClass):
    def __init__(self, w1, w2):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping
            sage: w, u = map(Words("abcdef"), ["ab", "cd"])
            sage: S = ShuffleProduct_overlapping(w,u)
            sage: S == loads(dumps(S))
            True
        """
        self._w1 = w1
        self._w2 = w2

    def __repr__(self):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping
            sage: w, u = map(Words("abcdef"), ["ab", "cd"])
            sage: ShuffleProduct_overlapping(w,u).__repr__()
            'Overlapping shuffle product of word: ab and word: cd'
        """
        return "Overlapping shuffle product of %s and %s"%(repr(self._w1), repr(self._w2))

    def __iter__(self):
        """
        EXAMPLES::

            sage: from sage.combinat.words.shuffle_product import ShuffleProduct_overlapping
            sage: w, u = map(Words(range(10)), [[0,1],[2,3]])
            sage: S = ShuffleProduct_overlapping(w,u)
            sage: S.list()
            [word: 0123, word: 0213, word: 0231, word: 2013, word: 2031, word: 2301, word: 213, word: 033, word: 231, word: 024, word: 231, word: 204, word: 24]

            sage: w, u = map(Words(range(1,10)), [[1,2],[3,4]])
            sage: S = ShuffleProduct_overlapping(w,u)
            sage: S.list()
            [word: 1234, word: 1324, word: 1342, word: 3124, word: 3142, word: 3412, word: 424, word: 154, word: 442, word: 136, word: 352, word: 316, word: 46]
        """
        m = len(self._w1)
        n = len(self._w2)
        for r in range(min(m,n)+1):
            for w in ShuffleProduct_overlapping_r(self._w1, self._w2, r):
                yield w