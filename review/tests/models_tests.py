"""Tests for the models of the review app."""
from django.test import TestCase
from django.utils.timezone import now, timedelta

from django_libs.tests.factories import UserFactory

from . import factories


class ReviewTestCase(TestCase):
    longMessage = True

    def setUp(self):
        self.review = factories.ReviewFactory()

    def test_instance(self):
        self.assertTrue(self.review.pk, msg=(
            'Review model should have been created.'))

    def test_get_user(self):
        self.assertEqual(self.review.get_user(), 'Anonymous', msg=(
            'Should return anonymous.'))
        self.user = UserFactory()
        self.review.user = self.user
        self.assertEqual(self.review.get_user(), self.user.email, msg=(
            'Should return a user\'s email.'))

    def test_get_average_rating(self):
        self.assertFalse(self.review.get_average_rating(), msg=(
            'If there are no ratings, it should return False.'))
        factories.RatingFactory(review=self.review, value='2')
        factories.RatingFactory(review=self.review, value='4')
        self.assertEqual(self.review.get_average_rating(), 3, msg=(
            'Should return the average rating value.'))

        factories.RatingFactory(review=self.review, value=None)
        factories.RatingFactory(category__counts_for_average=False,
                                review=self.review, value=0.0)
        self.assertEqual(self.review.get_average_rating(), 3, msg=(
            'Should return the average rating value and exclude the nullified'
            ' ones.'))

    def test_get_average_rating_with_custom_choices(self):
        self.assertFalse(self.review.get_average_rating(), msg=(
            'If there are no ratings, it should return False.'))
        rating1 = factories.RatingFactory(review=self.review, value='4')
        # we create choices to simulate, that the previous value was the max
        for i in range(0, 5):
            factories.RatingCategoryChoiceFactory(
                ratingcategory=rating1.category, value=i)
        rating2 = factories.RatingFactory(review=self.review, value='6')
        # we create choices to simulate, that the previous value was the max
        for i in range(0, 7):
            factories.RatingCategoryChoiceFactory(
                ratingcategory=rating2.category, value=i)
        # testing the absolute max voting
        self.assertEqual(self.review.get_average_rating(6), 6, msg=(
            'Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(4), 4, msg=(
            'Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(100), 100, msg=(
            'Should return the average rating value.'))

        # these ratings should not change results and should just be ignored
        factories.RatingFactory(
            category=rating2.category, review=self.review, value=None)
        factories.RatingFactory(review=self.review, value=None)
        self.assertEqual(self.review.get_average_rating(6), 6, msg=(
            'Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(4), 4, msg=(
            'Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(100), 100, msg=(
            'Should return the average rating value.'))

        # altering the ratings to get a very low voting
        rating1.value = '1'
        rating1.save()
        rating2.value = '1'
        rating2.save()
        self.assertEqual(self.review.get_average_rating(6), 1.1666666666666667,
                         msg=('Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(4), 0.7777777777777777,
                         msg=('Should return the average rating value.'))
        self.assertEqual(
            self.review.get_average_rating(100),
            19.444444444444446, msg=(
                'Should return the average rating value.'))

        # and finally the lowest possible voting
        rating1.value = '0'
        rating1.save()
        rating2.value = '0'
        rating2.save()
        self.assertEqual(self.review.get_average_rating(6), 0,
                         msg=('Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(4), 0,
                         msg=('Should return the average rating value.'))
        self.assertEqual(self.review.get_average_rating(100), 0,
                         msg=('Should return the average rating value.'))

    def test_is_editable(self):
        self.assertTrue(self.review.is_editable(), msg=(
            'Should be editable, if period setting is not set.'))
        with self.settings(REVIEW_UPDATE_PERIOD=1):
            self.assertTrue(self.review.is_editable(), msg=(
                'Should be editable, if period has not ended yet.'))
            self.review.creation_date = now() - timedelta(days=1)
            self.review.save()
            self.assertFalse(self.review.is_editable(), msg=(
                'Should return False, if period has ended.'))


class ReviewExtraInfoTestCase(TestCase):
    longMessage = True

    def setUp(self):
        self.extra_info = factories.ReviewExtraInfoFactory()

    def test_instance(self):
        self.assertTrue(self.extra_info.pk, msg=(
            'Review extra info model should have been created.'))


class RatingCategoryTestCase(TestCase):
    longMessage = True

    def setUp(self):
        self.category = factories.RatingCategoryFactory()

    def test_instance(self):
        self.assertTrue(self.category.pk, msg=(
            'Rating category model should have been created.'))


class RatingCategoryChoiceTestCase(TestCase):
    """Tests for the ``RatingCategoryChoice`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``RatingCategoryChoice`` model."""
        ratingcategorychoice = factories.RatingCategoryChoiceFactory()
        self.assertTrue(ratingcategorychoice.pk)


class RatingTestCase(TestCase):
    longMessage = True

    def setUp(self):
        self.rating = factories.RatingFactory()

    def test_instance(self):
        self.assertTrue(self.rating.pk, msg=(
            'Rating model should have been created.'))
