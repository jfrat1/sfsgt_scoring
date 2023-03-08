from ...src.course import Course, Tee, Hole

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
        Hole(num=i, par=par)
        for i, par in enumerate([
            4, 5, 4, 3, 4, 4, 3, 4, 5,
            5, 4, 4, 3, 4, 3, 4, 4, 5,
        ])
    ]
)

SHARP_PARK_WHITE_TEE = Tee(
    name="White",
    par=72,
    rating=70.3,
    slope=125,
    distance=6195,
)

SHARP_PARK = Course(
    name="Sharp Park",
    tees=[
        SHARP_PARK_WHITE_TEE,
    ],
    holes=[
        Hole(num=i, par=par)
        for i, par in enumerate([
            4, 4, 4, 5, 3, 4, 4, 3, 5,
            4, 4, 3, 5, 4, 3, 4, 4, 5,
        ])
    ]
)



