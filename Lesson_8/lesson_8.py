# Полет по фигурам с использованием функций и try/except

from djitellopy import Tello

# Создаем объект дрона
drone = Tello()

try:
    print("Подключение к дрону...")
    drone.connect()

    # Проверяем заряд батареи
    battery = drone.get_battery()
    print(f"Заряд батареи: {battery}%")

    # Проверка минимального заряда
    if battery < 20:
        print("Ошибка: слишком маленький заряд батареи!")
    else:
        print("Взлет...")
        drone.takeoff()


        # ---------------------------------------------------
        # Функция полета по фигуре
        # sides - количество сторон
        # steps - количество маленьких шагов
        # step_distance - длина одного шага
        # angle - угол поворота
        # ---------------------------------------------------
        def fly_shape(sides, steps, step_distance, angle):

            # Цикл по сторонам фигуры
            for side in range(sides):

                print(f"\nСторона {side + 1} из {sides}")

                # Внутренний цикл маленьких движений
                for step in range(steps):
                    print(
                        f"Шаг {step + 1}: "
                        f"летим вперед на {step_distance} см"
                    )

                    # Движение вперед
                    drone.move_forward(step_distance)

                # Поворот после стороны
                # На последней стороне поворот не нужен
                if side < sides - 1:
                    print(f"Поворот на {angle} градусов")

                    drone.rotate_clockwise(angle)


        # ---------------------------------------------------
        # КВАДРАТ
        # 4 стороны
        # ---------------------------------------------------
        # print("\n=== Полет по квадрату ===")
        #
        # fly_shape(
        #     sides=4,
        #     steps=3,
        #     step_distance=35,
        #     angle=90
        # )

        # ---------------------------------------------------
        # ТРЕУГОЛЬНИК
        # 3 стороны
        # ---------------------------------------------------
        print("\n=== Полет по треугольнику ===")

        fly_shape(
            sides=3,
            steps=2,
            step_distance=40,
            angle=120
        )

        print("\nПосадка...")
        drone.land()

# Ошибка подключения или команд
except Exception as error:

    print(f"\nПроизошла ошибка: {error}")

    # Пытаемся безопасно посадить дрон
    try:
        drone.land()
    except:
        print("Не удалось выполнить посадку")

# Этот блок выполнится всегда
finally:

    print("\nПрограмма завершена")
