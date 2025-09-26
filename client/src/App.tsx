import '@mantine/core/styles.css';

import { SummaryTextForm } from './components';
import { Box, Container, MantineProvider, Title, createTheme, type MantineColorsTuple } from '@mantine/core';

const myColor: MantineColorsTuple = [
  '#f1f4fe',
  '#e4e6ed',
  '#c8cad3',
  '#a9adb9',
  '#9094a3',
  '#7f8496',
  '#777c91',
  '#63687c',
  '#595e72',
  '#4a5167'
];

const theme = createTheme({
  colors: {
    myColor,
  },
});

function App() {

  return (
    <MantineProvider theme={theme}>
      <Box bg="myColor.9" mih="100dvh" w="100%">
        <Container>
            <Title c="myColor.0" ta="center">Avy Brief</Title>
            <SummaryTextForm />
        </Container>
      </Box>

    </MantineProvider>
  )
}

export default App
