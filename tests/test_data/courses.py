from ...src.classes import Course, Tee, Hole

PRESIDIO_BLUE_TEE = Tee(
    name='Blue',
    par=72,
    rating=69.5,
    slope=129,
    distance=5746,
)

PRESIDIO_WHITE_TEE = Tee(
    name='White',
    par=72,
    rating=71.1,
    slope=132,
    distance=6103,
)

PRESIDIO_BLACK_TEE = Tee(
    name='Black',
    par=72,
    rating=72.6,
    slope=135,
    distance=6481,
)

PRESIDIO = Course(
    name="Presidio",
    tees=[
        PRESIDIO_BLUE_TEE,
        PRESIDIO_WHITE_TEE,
        PRESIDIO_BLACK_TEE,
    ],
    holes=[
        Hole(num=1, par=4),
        Hole(num=2, par=5),
        Hole(num=3, par=4),
        Hole(num=4, par=3),
        Hole(num=5, par=4),
        Hole(num=6, par=4),
        Hole(num=7, par=3),
        Hole(num=8, par=4),
        Hole(num=9, par=5),
        Hole(num=10, par=5),
        Hole(num=11, par=4),
        Hole(num=12, par=4),
        Hole(num=13, par=3),
        Hole(num=14, par=4),
        Hole(num=15, par=3),
        Hole(num=16, par=4),
        Hole(num=17, par=4),
        Hole(num=18, par=5),
    ]
)