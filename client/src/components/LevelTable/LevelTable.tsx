import { Box, Flex, Title, Text, Badge } from "@mantine/core";
import type { DangerLevel, ElevBand, Prediction } from "../../types";

const levelColors: Record<DangerLevel, string> = {
    0: "myColor.1",
    1: "rgb(77, 184, 72)",
    2: "rgb(255, 242, 4)",
    3: "rgb(246, 147, 29)",
    4: "rgb(237, 29, 35)",
    5: "black",
}

const leveNames: Record<ElevBand, string> = {
    "below_treeline": "Below Treeline",
    "treeline": "Treeline",
    "above_treeline": "Above Treeline",
}

const mapLevels: Record<DangerLevel, string> = {
    0: "No Risk",
    1: "Low",
    2: "Moderate",
    3: "Considerable",
    4: "High",
    5: "Extreme"
}

const elevationSizes: Record<ElevBand, string> = {
    "below_treeline": "300px",
    "treeline": "200px",
    "above_treeline": "100px",
}

export function LevelTable({ prediction }: { prediction: Prediction }) {  

    return (
        <Box mb="lg">  
            <Title mb="xs" fz="lg" c="white">Danger Levels</Title>
            <Flex direction="column">
                {
                    ["above_treeline", "treeline", "below_treeline"].map((elevBand) => (
                        <Flex key={elevBand} justify="space-between" style={{ borderBottom: '1px solid var(--mantine-color-gray-3)' }}>
                            <Box w="33%" pb="xs">
                                <Text c="white">{leveNames[elevBand as ElevBand]}</Text>
                                <Badge color="white" c="black" size="sm">{prediction[elevBand as ElevBand]}</Badge>
                            </Box>
                            {
                                (prediction.scores && prediction.scores !== undefined) && (
                                    <Flex w="33%" direction="column">
                                        <Text c="myColor.2" fz="xs">Prediction Scores</Text>
                                        <Flex>
                                            {prediction.scores[elevBand as ElevBand].map((score, index) => (
                                                <Text fw={index === prediction[elevBand as ElevBand] ? "bold" : "normal"} c="white">{score.toFixed(2)}{index !== prediction!.scores![elevBand as ElevBand].length - 1 ? "," : ""}</Text>
                                            ))}
                                        </Flex>
                                    </Flex>
                                )
                            }
                            <Flex w="33%" align="center" justify="center">
                                <Box ta="center" p="xs" w={elevationSizes[elevBand as ElevBand]} bg={levelColors[prediction[elevBand as ElevBand]]}>
                                        <Badge color="white" c="black" size="sm">{mapLevels[prediction[elevBand as ElevBand]]}</Badge>
                                </Box>
                            </Flex>
                        </Flex>
                    ))
                }
            </Flex>
        </Box>
    );
}