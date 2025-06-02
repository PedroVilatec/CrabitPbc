#define WINDOW_SIZE 5

class PressureController {
  public:
    PressureController() : index(0), total(0) {}

    void updatePressure(int newPressure) {
      total -= pressures[index];
      pressures[index] = newPressure;
      total += newPressure;
      index = (index + 1) % WINDOW_SIZE;
    }

    int getSmoothPressure() {
      return total / WINDOW_SIZE;
    }

  private:
    int pressures[WINDOW_SIZE];
    int index;
    int total;
};