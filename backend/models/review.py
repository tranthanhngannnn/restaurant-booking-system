from core.extensions import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "Reviews"
    ReviewID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey("users.UserID"), nullable=False)
    RestaurantID = db.Column(db.Integer, db.ForeignKey("Restaurant.RestaurantID"), nullable=False)

    Rating = db.Column(db.Integer, nullable=False)
    Comment = db.Column(db.String(500), nullable=True)
    CreateAt = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('UserID', 'RestaurantID', name='unique_user_review'),
    )

    user = db.relationship("User", backref="reviews", lazy=True)
    restaurant = db.relationship("Restaurant", backref="reviews", lazy=True)
