#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Candy

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Images has to be path from static
# Add All Categories of Candies First

category1 = Category(name="Chocolate",description="Chocolate most commonly \
comes in dark, milk, and white varieties, with cocoa solids contributing \
to the brown color.", image='/static/images/category/Chocolate.jpg')

session.add(category1)
session.commit()

category2 = Category(name="Caramel",description="Caramel is a \
beige to dark-brown confectionery product made by heating a variety \
of sugars. ", image="/static/images/category/Caramels.jpg")

session.add(category2)
session.commit()

category3 = Category(name="Gummies",description="Gummi candy, \
gummy candy, gummies, or jelly sweets are a broad category of \
gelatin-based, chewy candies.", image="/static/images/category/gummies.jpeg")

session.add(category3)
session.commit()

category4 = Category(name="Marshmallow",description="A marshmallow is a \
sugar based candy that, in its modern form, typically\
 consists of sugar, whipped to a spongy consistency, molded into small\
 cylindrical pieces, and coated with corn starch.",
image="/static/images/category/marshmalow.jpg")

session.add(category4)
session.commit()

category5 = Category(name="Hard Candies",description="A hard candy, \
or boiled sweet, is a sugar candy prepared from one or more sugar-based \
syrups that is boiled to a temperature of 160C (320F) to make candy",
image="/static/images/category/hardcandies.jpg")

session.add(category5)
session.commit()

category6 = Category(name="Lollipops",description="A lollipop is a type \
of confectionery now consisting of a sweetmeat of hard candy or \
water-ice mounted on a stick and intended for sucking or licking.",
image="/static/images/category/lollipops.jpg")

session.add(category6)
session.commit()

category7 = Category(name="Sours",description="Sours are popular\
 for their cringe inducing flavor and acidity",
image="/static/images/category/sours.jpg")

session.add(category7)
session.commit()

# Add all the candies to bind the categories

# Chocolate Candies  (category1)
ChocoCandy1 = Candy(name="Kit-Kat",description="Chocolate-covered\
 wafer biscuit bar confection",
image="/static/images/candy/Kit-Kat.jpg", cavity="4.5", category = category1)

session.add(ChocoCandy1)
session.commit()

ChocoCandy2 = Candy(name="Maltesers",description="Spherical malt \
honeycomb centre, surrounded by milk chocolate",
image="/static/images/candy/maltesers.jpg", cavity="5", category = category1)

session.add(ChocoCandy2)
session.commit()

ChocoCandy3 = Candy(name="Snickers",description="Nougat topped with\
 caramel and peanuts",
image="/static/images/candy/Snickers.png", cavity="6.5", category = category1)

session.add(ChocoCandy3)
session.commit()

ChocoCandy4 = Candy(name="Twix",description="Biscuit applied with\
 other confectionery toppings and coatings",
image="/static/images/candy/Twix.jpg", cavity="4", category = category1)

session.add(ChocoCandy4)
session.commit()

ChocoCandy5 = Candy(name="Mars",description="Featuring nougat, soft caramel,\
almonds, and a milk chocolate coating",
image="/static/images/candy/mars.jpg", cavity="9", category = category1)

session.add(ChocoCandy5)
session.commit()

ChocoCandy6 = Candy(name="Cadbury Creme Egg",description="Milk chocolate shell,\
 housing a white and yellow fondant",
image="/static/images/candy/cadbury-egg.jpg", cavity="8.5", category = category1)

session.add(ChocoCandy6)
session.commit()

# Caramel Candies (category2)
CaramelCandy1 = Candy(name="Caramel squares",description="Soft caramel cubes",
image="/static/images/candy/caramels.jpg", cavity="6", category = category2)

session.add(CaramelCandy1)
session.commit()

CaramelCandy2 = Candy(name="Werther's Original",description="Caramel-flavoured\
 hard candy",
image="/static/images/candy/Werther.jpg", cavity="2", category = category2)

session.add(CaramelCandy2)
session.commit()

CaramelCandy3 = Candy(name="Tootsie Roll",description="Chewy chocolate candy",
image="/static/images/candy/tootsie.jpg", cavity="8.5", category = category2)

session.add(CaramelCandy3)
session.commit()

# Gummies Candies (category3)
GummyCandy1 = Candy(name="Twizzlers",description="Fruit-flavored candy sticks",
image="/static/images/candy/twizzler.jpg", cavity="4", category = category3)

session.add(GummyCandy1)
session.commit()

GummyCandy2 = Candy(name="Gummy bear",description="Small, fruit gum candy\
shaped in the form of a bear",
image="/static/images/candy/Gummy-bear.jpg", cavity="2.5", category = category3)

session.add(GummyCandy2)
session.commit()

GummyCandy3 = Candy(name="Gumdrop",description="Brightly colored gelatin\
or pectin-based pieces, shaped like a truncated cone and coated in granulated\
sugar",
image="/static/images/candy/gumdrops.jpg", cavity="5", category = category3)

session.add(GummyCandy3)
session.commit()

GummyCandy4 = Candy(name="Dots",description="Chewable, cone-shaped treats",
image="/static/images/candy/dots.jpg", cavity="2.5", category = category3)

session.add(GummyCandy4)
session.commit()

# Marshmallow Candies (category4)
MallowCandy1 = Candy(name="Peeps",description="Peeps are marshmallow \
candies that are shaped into chicks, bunnies, and other animals",
image="/static/images/candy/peeps.jpg", cavity="6", category = category4)

session.add(MallowCandy1)
session.commit()

MallowCandy2 = Candy(name="Marshmallow Ice Cream Cone",description="Crunchy\
marshmallow ice cream candy cones in assorted colors and flavors",
image="/static/images/candy/cone.jpg", cavity="5.5", category = category4)

session.add(MallowCandy2)
session.commit()


# Hard Candies Candies (category5)
HardCandy1 = Candy(name="Butterscotch",description="Type of \
confectionery whose primary ingredients are brown sugar and butter",
image="/static/images/candy/Butterscotch.jpg", cavity="1.5", category = category5)

session.add(HardCandy1)
session.commit()

HardCandy2 = Candy(name="Candy cane",description="Traditional Christmas\
treat, peppermint flavored. Cane shape allows them to be hung on a \
Christmas tree. Usually white with red streaks.",
image="/static/images/candy/Cane.jpg", cavity="2.5", category = category5)

session.add(HardCandy2)
session.commit()

HardCandy3 = Candy(name="Life Savers",description="Ring-shaped\
mints and artificially fruit-flavored hard candy.",
image="/static/images/candy/life-savers.jpg", cavity="3", category = category5)

session.add(HardCandy3)
session.commit()

HardCandy4 = Candy(name="Sweethearts",description="Small heart-shaped candies\
 They are often jasmine-flavored.",
image="/static/images/candy/SweetHearts.jpg", cavity="2", category = category5)

session.add(HardCandy4)
session.commit()


# Lollipops Candies (category6)
LollipopCandy1 = Candy(name="Dum Dums",description="Sphere-shaped lollipops.",
image="/static/images/candy/Dum_Dums.jpg", cavity="4", category = category6)

session.add(LollipopCandy1)
session.commit()

LollipopCandy2 = Candy(name="Chupa Chups",description="Type of confectionery\
consisting mainly of hardened, flavored sucrose with corn syrup mounted \
on a stick.",
image="/static/images/candy/chupa-chups.jpg", cavity="3.5", category = category6)

session.add(LollipopCandy2)
session.commit()

# Sours Candies (category7)
SoursCandy1 = Candy(name="Sour Patch Kids",description="Soft candy with a\
coating of sour sugar.", image="/static/images/candy/Sour-Patch-Kids.jpg",
                    cavity="6",
                    category = category7)

session.add(SoursCandy1)
session.commit()

SoursCandy2 = Candy(name="Warheads",description="Sour fruit flavors. \
'Extreme' candy with an intense sour flavor",
                    image="/static/images/candy/warheads.jpg",
                    cavity="6",
                    category = category7)

session.add(SoursCandy2)
session.commit()

print "Trick or treath!"




