use std::fmt;
use std::str::FromStr;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NoteName {
    C,
    Db,
    D,
    Eb,
    E,
    F,
    Gb,
    G,
    Ab,
    A,
    Bb,
    B,
}

impl NoteName {
    pub fn semitone(self) -> i32 {
        match self {
            NoteName::C => 0,
            NoteName::Db => 1,
            NoteName::D => 2,
            NoteName::Eb => 3,
            NoteName::E => 4,
            NoteName::F => 5,
            NoteName::Gb => 6,
            NoteName::G => 7,
            NoteName::Ab => 8,
            NoteName::A => 9,
            NoteName::Bb => 10,
            NoteName::B => 11,
        }
    }
}

impl FromStr for NoteName {
    type Err = String;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value.trim().to_ascii_lowercase().as_str() {
            "c" => Ok(NoteName::C),
            "c#" | "db" => Ok(NoteName::Db),
            "d" => Ok(NoteName::D),
            "d#" | "eb" => Ok(NoteName::Eb),
            "e" | "fb" => Ok(NoteName::E),
            "f" | "e#" => Ok(NoteName::F),
            "f#" | "gb" => Ok(NoteName::Gb),
            "g" => Ok(NoteName::G),
            "g#" | "ab" => Ok(NoteName::Ab),
            "a" => Ok(NoteName::A),
            "a#" | "bb" => Ok(NoteName::Bb),
            "b" | "cb" => Ok(NoteName::B),
            other => Err(format!("unknown note '{other}'")),
        }
    }
}

impl fmt::Display for NoteName {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            NoteName::C => "C",
            NoteName::Db => "Db",
            NoteName::D => "D",
            NoteName::Eb => "Eb",
            NoteName::E => "E",
            NoteName::F => "F",
            NoteName::Gb => "Gb",
            NoteName::G => "G",
            NoteName::Ab => "Ab",
            NoteName::A => "A",
            NoteName::Bb => "Bb",
            NoteName::B => "B",
        };
        f.write_str(name)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Scale {
    Major,
    Minor,
    Chromatic,
    PentatonicMajor,
    PentatonicMinor,
}

impl Scale {
    pub fn semitones(self) -> &'static [i32] {
        match self {
            Scale::Major => &[0, 2, 4, 5, 7, 9, 11],
            Scale::Minor => &[0, 2, 3, 5, 7, 8, 10],
            Scale::Chromatic => &[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            Scale::PentatonicMajor => &[0, 2, 4, 7, 9],
            Scale::PentatonicMinor => &[0, 3, 5, 7, 10],
        }
    }
}

impl FromStr for Scale {
    type Err = String;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value.trim().to_ascii_lowercase().replace('-', "_").as_str() {
            "major" | "maj" => Ok(Scale::Major),
            "minor" | "min" | "natural_minor" => Ok(Scale::Minor),
            "chromatic" | "all" => Ok(Scale::Chromatic),
            "pentatonic_major" | "major_pentatonic" | "maj_pent" => Ok(Scale::PentatonicMajor),
            "pentatonic_minor" | "minor_pentatonic" | "min_pent" => Ok(Scale::PentatonicMinor),
            other => Err(format!("unknown scale '{other}'")),
        }
    }
}

impl fmt::Display for Scale {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Scale::Major => "major",
            Scale::Minor => "minor",
            Scale::Chromatic => "chromatic",
            Scale::PentatonicMajor => "pentatonic-major",
            Scale::PentatonicMinor => "pentatonic-minor",
        };
        f.write_str(name)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Key {
    pub root: NoteName,
    pub scale: Scale,
}

impl Key {
    pub fn parse(root: &str, scale: &str) -> Result<Self, String> {
        Ok(Self {
            root: root.parse()?,
            scale: scale.parse()?,
        })
    }

    pub fn nearest_midi(self, midi_note: f32) -> f32 {
        let root = self.root.semitone();
        let octave = (midi_note / 12.0).floor() as i32;
        let mut best = midi_note.round();
        let mut best_distance = f32::INFINITY;

        for octave_offset in -1..=1 {
            for interval in self.scale.semitones() {
                let candidate = ((octave + octave_offset) * 12 + root + interval) as f32;
                let distance = (candidate - midi_note).abs();
                if distance < best_distance {
                    best = candidate;
                    best_distance = distance;
                }
            }
        }

        best
    }
}

pub fn hz_to_midi(hz: f32, concert_a: f32) -> f32 {
    69.0 + 12.0 * (hz / concert_a).log2()
}

pub fn midi_to_hz(midi: f32, concert_a: f32) -> f32 {
    concert_a * 2.0_f32.powf((midi - 69.0) / 12.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_enharmonic_keys() {
        assert_eq!("C#".parse::<NoteName>().unwrap(), NoteName::Db);
        assert_eq!("Bb".parse::<NoteName>().unwrap(), NoteName::Bb);
        assert_eq!(
            "minor-pentatonic".parse::<Scale>().unwrap(),
            Scale::PentatonicMinor
        );
    }

    #[test]
    fn snaps_to_key_notes() {
        let key = Key::parse("C", "major").unwrap();
        let slightly_sharp_c = 60.18;
        let between_c_and_db = 60.49;
        let db_in_c_major = 61.0;

        assert_eq!(key.nearest_midi(slightly_sharp_c), 60.0);
        assert_eq!(key.nearest_midi(between_c_and_db), 60.0);
        assert_eq!(key.nearest_midi(db_in_c_major), 60.0);
    }
}
