from flask import jsonify, Blueprint, abort

from flask.ext.restful import (Resource, Api, reqparse, inputs, fields,
                               marshal, marshal_with, url_for)

import models

review_fields = {
    'id': fields.Integer,
    'for_course': fields.String,
    'rating': fields.Integer,
    'comment': fields.String(default=''),
    'created_at': fields.DateTime
}


def review_or_404(review_id):
    try:
        review = models.Review.get(models.Review.id==review_id)
    except models.Course.DoesNotExist:
        abort(404)
    else:
        return review

def add_course(review):
    review.for_course = url_for('resources.courses.course', id=review.course.id)
    return review


class ReviewList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('course',
            required=True,
            help='No course provided',
            location=['form', 'json'],
            type=inputs.positive)
        self.reqparse.add_argument('rating',
            required=True,
            help='No course rating provided',
            location=['form', 'json'],
            type=inputs.int_range(1, 5))
        self.reqparse.add_argument('comment',
            required=False,
            nullable=True,
            location=['form', 'json'],
            default='')
        super().__init__()

    def get(self):
        reviews = [marshal(add_course(review), review_fields)
            for review in models.Review.select()]
        return {'reviews': reviews}

    @marshal_with(review_fields)
    def post(self):
        args = self.reqparse.parse_args()
        review = models.Review.create(**args)
        return (add_course(review), 201, {
            'Location': url_for('resources.reviews.review', id=review.id)})


class Review(Resource):
    @marshal_with(review_fields)
    def get(self, id):
        return add_course(review_or_404(id))

    @marshal_with(review_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        query = models.Review.update(**args).where(models.Review.id==id)
        query.execute()
        return (add_course(models.Review.get(models.Review.id==id)), 200,
                {'Location': url_for('resources.reviews.review')})

    def delete(self, id):
        query = models.Review.delete().where(models.Review.id==id)
        query.execute()
        return ('', 204, {'Location': url_for('resources.reviews.review')})

reviews_api = Blueprint('resources.reviews', __name__)
api = Api(reviews_api)
api.add_resource(ReviewList, '/reviews', endpoint='reviews')
api.add_resource(Review, '/reviews/<int:id>', endpoint='review')
