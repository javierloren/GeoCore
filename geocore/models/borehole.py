from dataclasses import dataclass, field


@dataclass
class LithologyInterval:
    from_m: float
    to_m: float
    lithology: str = ""
    description: str = ""
    weathering: str = ""
    strength: str = ""
    notes: str = ""


@dataclass
class CoreRun:
    from_m: float
    to_m: float
    recovered_length_m: float | None = None
    rqd_percent: float | None = None
    photo_id: str | None = None
    validated: bool = False

    @property
    def run_length_m(self) -> float:
        return max(0.0, self.to_m - self.from_m)

    @property
    def recovery_percent(self) -> float | None:
        if self.recovered_length_m is None or self.run_length_m == 0:
            return None
        return 100.0 * self.recovered_length_m / self.run_length_m


@dataclass
class Borehole:
    borehole_id: str
    x: float | None = None
    y: float | None = None
    z: float | None = None
    final_depth_m: float | None = None
    inclination_deg: float = 90.0
    azimuth_deg: float | None = None
    groundwater_depth_m: float | None = None
    lithology: list[LithologyInterval] = field(default_factory=list)
    core_runs: list[CoreRun] = field(default_factory=list)


@dataclass
class Project:
    name: str
    client: str = ""
    location: str = ""
    coordinate_reference_system: str = ""
    notes: str = ""
    boreholes: list[Borehole] = field(default_factory=list)

